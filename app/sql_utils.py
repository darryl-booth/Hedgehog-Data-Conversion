from pathlib import Path
import re

SCHEMA_DIR = Path(__file__).resolve().parent.parent / 'schema'

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
    return text


def get_table_columns(table_name: str):
    text = _read_latest_sql_file()
    lines = text.splitlines()

    start_re = re.compile(rf"^CREATE TABLE \[dbo\]\.\[{re.escape(table_name)}\]\(", re.IGNORECASE)
    start_idx = None
    for i, line in enumerate(lines):
        if start_re.search(line):
            start_idx = i + 1
            break

    if start_idx is None:
        raise SchemaError(f'Table {table_name} not found in schema')

    columns = []
    for line in lines[start_idx:]:
        stripped = line.strip().rstrip(',')
        if not stripped or stripped.upper().startswith('CONSTRAINT'):
            break
        m = re.match(r"\[(?P<name>[^\]]+)\]\s+(?P<type>\w+(?:\([^\)]*\))?)", stripped)
        if m:
            columns.append({'field': m.group('name'), 'type': m.group('type')})

    return columns
