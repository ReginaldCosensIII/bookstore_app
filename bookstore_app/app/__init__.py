from flask import Flask
from .routes import bp as main_bp

def create_app():    
    # Create a Flask application instance.
    # Register the main blueprint with the application.
    app = Flask(__name__, template_folder="templates")
    app.register_blueprint(main_bp)
    return app
