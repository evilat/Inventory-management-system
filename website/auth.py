from flask import Blueprint, render_template
from . import db

auth = Blueprint('auth', __name__)