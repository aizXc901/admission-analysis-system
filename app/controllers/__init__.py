"""
Controller module initialization
"""
from flask import Blueprint

bp = Blueprint('main', __name__)

from . import main_controller