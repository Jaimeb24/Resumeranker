"""Database initialization and management."""

from flask import Flask
from models import db

def init_db(app: Flask):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables if they don't exist
        db.create_all()
        print("Database tables created successfully!")

def get_db():
    """Get the database instance."""
    return db
