from . import app
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')
from flask import jsonify
from .sql_utils import get_table_columns, SchemaError


@app.route('/schema/<table_name>')
def schema(table_name):
    try:
        columns = get_table_columns(table_name)
        return jsonify(columns)
    except SchemaError as e:
        return jsonify({'error': str(e)}), 400

