from pathlib import Path
import re
import sqlite3

SCHEMA_DIR = Path(__file__).resolve().parent.parent / 'schema'
DB_PATH = Path(__file__).resolve().parent / 'schema_cache.sqlite'

class SchemaError(Exception):
    pass


def _read_latest_sql_file():
    sql_files = list(SCHEMA_DIR.glob('*.sql'))
    if not sql_files:
        raise SchemaError('No SQL files found in schema directory')
    latest = max(sql_files, key=lambda p: p.stat().st_mtime)
    with latest.open('rb') as f:
        data = f.read()
    # detect UTF-16 LE/BE BOM
    if data.startswith(b'\xff\xfe'):
        text = data.decode('utf-16le')
    elif data.startswith(b'\xfe\xff'):
        text = data.decode('utf-16be')
    else:
        text = data.decode('utf-8')
    return text, latest.stat().st_mtime


def _parse_schema(text: str):
    """Parse the SQL text and yield (table, field, type) tuples."""
    lines = text.splitlines()
    results = []
    i = 0
    table_re = re.compile(r"^CREATE TABLE \[dbo\]\.\[(?P<table>[^\]]+)\]\s*\(", re.IGNORECASE)
    while i < len(lines):
        m = table_re.search(lines[i])
        if m:
            table = m.group('table')
            i += 1
            while i < len(lines):
                stripped = lines[i].strip().rstrip(',')
                if not stripped or stripped.upper().startswith('CONSTRAINT'):
                    break
                cm = re.match(r"\[(?P<name>[^\]]+)\]\s+(?P<type>\w+(?:\([^\)]*\))?)", stripped)
                if cm:
                    results.append((table, cm.group('name'), cm.group('type')))
                i += 1
        else:
            i += 1
    return results


def _ensure_db(text: str, mtime: float):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with conn:
        conn.execute(
            'CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)'
        )
        conn.execute(
            'CREATE TABLE IF NOT EXISTS columns (table_name TEXT, field_name TEXT, data_type TEXT)'
        )
        cur = conn.execute(
            "SELECT value FROM metadata WHERE key='schema_mtime'"
        )
        row = cur.fetchone()
        if row and float(row[0]) == mtime:
            return
        conn.execute('DELETE FROM columns')
        for table, field, dtype in _parse_schema(text):
            conn.execute(
                'INSERT INTO columns(table_name, field_name, data_type) VALUES(?,?,?)',
                (table, field, dtype),
            )
        conn.execute(
            'REPLACE INTO metadata(key, value) VALUES(?, ?)',
            ('schema_mtime', str(mtime)),
        )
    conn.close()


def initialize_schema_cache():
    text, mtime = _read_latest_sql_file()
    _ensure_db(text, mtime)


def get_table_columns(table_name: str):
    conn = sqlite3.connect(DB_PATH)
    with conn:
        rows = conn.execute(
            'SELECT field_name, data_type FROM columns WHERE table_name=?',
            (table_name,),
        ).fetchall()
    conn.close()
    if not rows:
        raise SchemaError(f'Table {table_name} not found in schema')
    return [{'field': r[0], 'type': r[1]} for r in rows]
