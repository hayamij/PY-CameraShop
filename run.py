"""
Flask Camera Shop Application Entry Point
Clean Architecture Implementation
"""
import os
from app.infrastructure.factory import create_app
from app.infrastructure.database.db import db

# Create Flask application
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """Create shell context for flask shell command"""
    return {
        'db': db,
        'app': app
    }


if __name__ == '__main__':
    # Run the application
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=app.config['DEBUG']
    )
