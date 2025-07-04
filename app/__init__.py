from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()  # Load environment variables from .env
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    from . import api
    app.register_blueprint(api.bp)

    return app
