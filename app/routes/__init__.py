"""
FLYTAU Routes Registration
Imports and registers all route modules with the Flask app
"""


def register_routes(app):
    """
    Register all route modules with the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Import route modules
    from .auth_routes import register_auth_routes
    from .flight_routes import register_flight_routes
    from .order_routes import register_order_routes
    from .admin_routes import register_admin_routes
    from .report_routes import register_report_routes
    
    # Register each module's routes
    register_auth_routes(app)
    register_flight_routes(app)
    register_order_routes(app)
    register_admin_routes(app)
    register_report_routes(app)
    
    # Register home route
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
