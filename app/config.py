"""
Configuration module for the Game Recommendation System.
This module handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv

# Get the absolute path of the current directory
basedir = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from .env file in the parent directory
load_dotenv(os.path.join(basedir, '..', '.env'))

class Config:
    """
    Configuration class that holds all application settings.
    Settings can be overridden by environment variables.
    """
    # Secret key for session management and security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Path to the data directory where datasets are stored
    DATA_FOLDER = os.path.join(basedir, '..', 'data')
    
    # Path to the models directory where trained models are saved
    MODEL_FOLDER = os.path.join(basedir, '..', 'models') 