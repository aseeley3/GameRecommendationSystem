"""
Main routes module for the Game Recommendation System.
This module handles all the web routes and API endpoints.
"""

from flask import Blueprint, render_template, request, jsonify
from app.services.recommender import get_recommendations
import pandas as pd
import pickle

# Create a Blueprint for the main routes
bp = Blueprint('main', __name__)

games_df = pd.read_csv('data_processing/steam_filtered.csv')
media_df = pd.read_csv('data_processing/steam_media_data_filtered.csv')
trailer_df = pd.read_csv('data_processing/steam_trailers.csv')
descriptions_df = pd.read_csv('data_processing/steam_description_data_filtered.csv')

merged_df = (games_df
             .merge(media_df, on='appid')
             .merge(trailer_df, on='appid')
             .merge(descriptions_df, on='appid'))

games = merged_df.to_dict(orient='records')

with open('data_processing/ids_to_reviews.pkl', 'rb') as f:
    reviews_dict = pickle.load(f)

@bp.route('/')
def index():
    """
    Home page route.
    Renders the main search interface where users can find game recommendations.
    
    Returns:
        Rendered template: The index.html template with the search interface
    """
    return render_template('index.html')

@bp.route('/recommend', methods=['GET'])
def recommend():
    platform = request.args.get('platform', 'all')
    # Here you would use the platform to filter game recommendations
    return render_template('recommend.html', platform=platform)

@bp.route('/select-platform', methods=['GET', 'POST'])
def select_platform():
    if request.method == 'POST':
        selected_platforms = request.form.getlist('platform')
        # Process selected platforms as needed
        return render_template('select_favoritres.html', platforms=selected_platforms)
    return render_template('select_platform.html')

@bp.route('/select-favorites', methods=['GET', 'POST'])
def select_favorites():
    # Get offset from query parameter (default to 0)
    offset = int(request.args.get('offset', 0))
    page_size = 50

    # Sort games by review count
    sorted_games = sorted(
        games,
        key=lambda game: len(reviews_dict.get(game['appid'], [])),
        reverse=True
    )

    next_offset = offset + page_size if offset + page_size < len(sorted_games) else None
    previous_offset = max(offset - page_size, 0) if offset > 0 else None

    # Paginate games
    paginated_games = sorted_games[offset:offset + page_size]

    # Render with current page of games
    return render_template(
        'select_favorites.html',
        games=paginated_games,
        next_offset=next_offset,
        previous_offset=previous_offset
        )