from flask import Flask
from flask_session import Session
import os
from .sql_utils import initialize_schema_cache

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

initialize_schema_cache()

from . import routes
