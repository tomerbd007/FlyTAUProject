"""Main Flask app setup - creates and configures the application."""
from flask import Flask
from .config import Config

# Export register_error_handlers for use in application.py (EB entrypoint)
__all__ = ['create_app', 'register_error_handlers']


def create_app(config_class=Config):
    """Sets up Flask with all the routes, DB connection, and error handlers."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    from . import db
    db.init_app(app)
    
    from .routes import register_routes
    register_routes(app)
    
    register_error_handlers(app)
    
    return app


def register_error_handlers(app):
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        return render_template('errors/500.html'), 500
