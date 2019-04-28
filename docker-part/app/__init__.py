from flask import Flask

app = Flask(__name__)

from app import general_routes
from app import highauth_routes
from app import univ_routes
from app import stud_routes
from app import entity_routes
