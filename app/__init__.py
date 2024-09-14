# mm-shopping-cart/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv
from .swagger import configure_swagger
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)
    load_dotenv()

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://marketmaster:password@mm-shopping-cart-db:5432/marketmaster'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Configure Swagger and get the API instance
    api = configure_swagger(app)

    # Import and register the API routes
    from .api.routes import init_routes
    init_routes(api)

    return app
