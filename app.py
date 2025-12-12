"""
Main entry point for the Camera Shop application
Run this file to start the Flask development server
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
