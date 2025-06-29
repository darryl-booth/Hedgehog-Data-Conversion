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
    # regex to capture CREATE TABLE statement
    pattern = rf"CREATE TABLE \[dbo\]\.\[{re.escape(table_name)}\]\((.*?)\)\s*CONSTRAINT"
    match = re.search(pattern, text, re.S | re.IGNORECASE)
    if not match:
        raise SchemaError(f'Table {table_name} not found in schema')
    body = match.group(1)
    columns = []
    for line in body.splitlines():
        line = line.strip().rstrip(',')
        if not line or line.upper().startswith('CONSTRAINT'):
            continue
        m = re.match(r"\[(?P<name>[^\]]+)\]\s+(?P<type>\w+(?:\([^\)]*\))?)", line)
        if m:
            columns.append({'field': m.group('name'), 'type': m.group('type')})
    return columns
