from flask import Flask
from flask_session import Session
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

from . import routes
