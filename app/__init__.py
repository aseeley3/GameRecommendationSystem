from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions here if needed

    # Register blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app 