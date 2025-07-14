"""
Main routes module for the Game Recommendation System.
This module handles all the web routes and API endpoints.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.services.recommender import get_recommendations
from app.services.platform_service import create_platform_service
from app.services.genre_header_service import create_genre_service
import pandas as pd
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Create a Blueprint for the main routes
bp = Blueprint('main', __name__)

games_df = pd.read_csv('data_processing/steam_filtered.csv')
media_df = pd.read_csv('data_processing/steam_media_data_filtered.csv')
trailer_df = pd.read_csv('data_processing/steam_trailers.csv')
descriptions_df = pd.read_csv('data_processing/steam_description_data_filtered.csv')

merged_df = (games_df
             .merge(media_df, on='appid', how='left')
             .merge(trailer_df, on='appid', how='left')  # <- preserves games even if trailer is missing
             .merge(descriptions_df, on='appid', how='left'))

games = merged_df.to_dict(orient='records')
games_dict = {game['appid']: game for game in games}

with open('data_processing/ids_to_reviews.pkl', 'rb') as f:
    reviews_dict = pickle.load(f)

with open("data_processing/description_fallback_embeddings.pkl", "rb") as f:
    embeddings_dict = pickle.load(f)

def age_filter(game, user_age):
    try:
        required_age = int(game.get('required_age', 0))
    except (ValueError, TypeError):
        required_age = 0

    return user_age >= required_age

@bp.route('/')
def index():
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
        return render_template('select_favorites.html', platforms=selected_platforms)
    return render_template('select_platform.html')

@bp.route('/select_favorites', methods=['GET', 'POST'])
def select_favorites():
    offset = 0
    page_size = 20
    platform = request.args.get('platform', 'all')
    genre = request.args.get('genre', 'all')
    age = int(request.args.get('age') or 0)

    # Create services for filtering
    platform_service = create_platform_service(games)
    genre_service = create_genre_service(games)

    # Start with all games
    filtered_games = games

    # Filter by platform first
    
    # Initialize selected games from session
    if 'selected_games' not in session:
        session['selected_games'] = []
    selected = set(int(appid) for appid in session['selected_games'])
    
    if platform != 'all':
        filtered_games = platform_service.filter_games_by_platform(platform)

    # Then filter by genre on the already filtered games
    if genre != 'all':
        # Create a new genre service with the already filtered games
        genre_service_filtered = create_genre_service(filtered_games)
        filtered_games = genre_service_filtered.filter_games_by_genre(genre)

    age_filtered_games = [
    game for game in filtered_games if age_filter(game, age)
    ]

    # Sort games by review count
    sorted_games = sorted(
        age_filtered_games,
        key=lambda game: len(reviews_dict.get(game['appid'], [])),
        reverse=True
    )

    # --- IMPORTANT: read name filter from args for both GET and POST ---
    name_filter = request.args.get('name', '').lower().strip()

    if request.method == 'POST':
        form = request.form
        action = form.get('action')
        offset = int(form.get('offset', 0))
        # Handle add/remove selection from POST
        appid_str = form.get('appid')

        if appid_str and appid_str.isdigit():
            appid = int(appid_str)
            if action == 'add':
                selected.add(appid)
            elif action == 'remove':
                selected.discard(appid)
            print(selected)
            print(len(selected))
            session['selected_games'] = list(selected)

        # Handle pagination buttons via form 'action'
        if action == 'Next →':
            offset += page_size
        elif action == '← Previous':
            offset = max(offset - page_size, 0)

        # Handle continue action
        if 'continue' in form and len(selected) >= 5:
         return redirect(url_for(
        'main.recommendations',
        platform=platform,
        genre=genre,
        age=age,
        name=name_filter if name_filter else None
            ))
    else:
        # For GET requests, get offset from query params
        offset = int(request.args.get('offset', 0))

    # Filter games by name if present
    if name_filter:
        sorted_games = [game for game in sorted_games if name_filter in game['name'].lower()]

    # Paginate games
    paginated_games = sorted_games[offset:offset + page_size]
    next_offset = offset + page_size if offset + page_size < len(sorted_games) else None
    previous_offset = max(offset - page_size, 0) if offset > 0 else None

    # Prepare selected games details for template
    selected_games_details = []
    for game_id in selected:
        game_info = games_dict.get(game_id)
        if game_info:
            game_platforms = game_info.get('platforms', 'Unknown')
            selected_games_details.append({
                'id': game_id,
                'name': game_info.get('name', 'Unknown'),
                'platforms': game_platforms,
                'on_current_platform': platform == 'all' or (game_platforms and platform in game_platforms.lower())
            })

    return render_template(
        'select_favorites.html',
        games=paginated_games,
        next_offset=next_offset,
        previous_offset=previous_offset if offset > 0 else None,
        offset=offset,
        selected=selected,
        total_selected_count=len(selected),
        current_platform=platform,
        current_genre=genre,
        age = age,
        selected_games_details=selected_games_details,
        show_genre_filter=True,
        name_filter=name_filter# Show genre filter on favorites page
        )


@bp.route('/update-game-selection', methods=['POST'])
def update_game_selection():
    try:
        game_id = int(request.form.get('selected_games'))
        is_checked = request.form.get('checked') == 'true'

        # Initialize session if needed
        if 'selected_games' not in session:
            session['selected_games'] = []

        # Get current selected games
        selected_games = set(int(appid) for appid in session.get('selected_games', []))

        # Update selection
        if is_checked:
            selected_games.add(game_id)
        else:
            selected_games.discard(game_id)

        # Save back to session
        session['selected_games'] = list(selected_games)

        return jsonify({
            'success': True,
            'total_count': len(session['selected_games']),
            'selected_games': session['selected_games']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@bp.route('/api/genres')
def get_genres():
    """API endpoint to get all available genres from the dataset."""
    try:
        genre_service = create_genre_service(games)
        # Get more genres to ensure we don't miss shooter subgenres
        all_genres = genre_service.get_popular_genres(limit=100)  # Get top 100 genres

        # Prioritize shooter-related genres and other important ones
        shooter_keywords = ['shooter', 'fps', 'shoot', 'gun', 'combat', 'war']
        important_genres = ['Action', 'Adventure', 'RPG', 'Strategy', 'Simulation', 'Sports', 'Racing', 'Puzzle', 'Platformer', 'Fighting', 'Horror', 'Survival', 'Sandbox', 'MMORPG', 'Indie', 'Casual', 'Multiplayer']

        # Separate genres into categories
        shooter_genres = []
        important_genre_list = []
        other_genres = []

        for genre in all_genres:
            genre_name_lower = genre['name'].lower()
            if any(keyword in genre_name_lower for keyword in shooter_keywords):
                shooter_genres.append(genre)
            elif genre['name'] in important_genres:
                important_genre_list.append(genre)
            else:
                other_genres.append(genre)

        # Debug: Log what shooter genres we found
        print(f"DEBUG: Found {len(shooter_genres)} shooter genres:")
        for sg in shooter_genres:
            print(f"  - {sg['name']}: {sg['count']} games")

        # Combine: important genres first, then shooter genres, then others (limit to ~50 total)
        final_genres = important_genre_list[:20] + shooter_genres + other_genres[:20]

        # Format for frontend consumption
        genres_data = [
            {
                'name': genre['name'],
                'display': genre['name'],
                'count': genre['count']
            }
            for genre in final_genres
        ]

        return jsonify({
            'success': True,
            'genres': genres_data,
            'debug': {
                'total_genres_found': len(all_genres),
                'shooter_genres_count': len(shooter_genres),
                'important_genres_count': len(important_genre_list),
                'other_genres_count': len(other_genres),
                'final_count': len(final_genres)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/debug/all-genres')
def debug_all_genres():
    """Debug endpoint to see all genres in the dataset."""
    try:
        genre_service = create_genre_service(games)
        all_genres = genre_service.get_popular_genres(limit=200)  # Get many genres

        # Find shooter genres specifically
        shooter_keywords = ['shooter', 'fps', 'shoot', 'gun', 'combat', 'war']
        shooter_genres = []
        for genre in all_genres:
            if any(keyword in genre['name'].lower() for keyword in shooter_keywords):
                shooter_genres.append(genre)

        return jsonify({
            'success': True,
            'total_count': len(all_genres),
            'shooter_count': len(shooter_genres),
            'shooter_genres': [{'name': g['name'], 'count': g['count']} for g in shooter_genres],
            'all_genres': [{'name': g['name'], 'count': g['count']} for g in all_genres[:50]]  # First 50 for brevity
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    # Get offset from query parameter (default to 0)
    offset = int(request.args.get('offset', 0))
    page_size = 20

    platform = request.args.get('platform', 'all')
    genre = request.args.get('genre', 'all')
    name_filter = request.args.get('name', '').lower().strip()
    age = int(request.args.get('age') or 0)

    game_ids = list(embeddings_dict.keys())

    all_embeddings = np.array([embeddings_dict[game] for game in game_ids])

    target_games = session['selected_games']

    # Check that all target games are in the embeddings dictionary
    missing = [gid for gid in target_games if gid not in embeddings_dict]
    if missing:
        raise ValueError(f"Games not found in embeddings: {missing}")

    # Collect their embeddings
    target_embeddings = [embeddings_dict[gid] for gid in target_games]

    # Stack into a single 2D array: shape (num_games, embedding_dim)
    if len(target_games) > 1:
        target_embeddings_array = np.vstack(target_embeddings)
        mean_embedding = target_embeddings_array.mean(axis=0)
        mean_embedding = mean_embedding.reshape(1, -1)
    else:
        mean_embedding = target_embeddings[0].reshape(1, -1)

    similarities = cosine_similarity(mean_embedding, all_embeddings)[0]

    # Pair game names with their similarity scores
    game_scores = list(zip(game_ids, similarities))

    # Sort by similarity (highest first)
    game_scores.sort(key=lambda x: x[1], reverse=True)

    # Optionally skip the first result if it's the game itself (similarity 1.0)
    recommendations = [(g, s) for g, s in game_scores if g not in target_games and g in games_dict]

    selected_games = []
    for game_id, similarity in recommendations:
        game = games_dict.get(game_id)
        if game:
            game_copy = game.copy()
            game_copy['similarity'] = similarity
            selected_games.append(game_copy)

    # Apply platform filter
    if platform != 'all':
        platform_service = create_platform_service(selected_games)
        selected_games = platform_service.filter_games_by_platform(platform)

    # Apply genre filter
    if genre != 'all':
        genre_service = create_genre_service(selected_games)
        selected_games = genre_service.filter_games_by_genre(genre)

    # Apply age filter
    selected_games = [game for game in selected_games if age_filter(game, age)]

    # Apply name search filter
    if name_filter:
        selected_games = [game for game in selected_games if name_filter in game['name'].lower()]


    next_offset = offset + page_size if offset + page_size < len(selected_games) else None
    previous_offset = max(offset - page_size, 0) if offset > 0 else None

    # Paginate games
    paginated_games = selected_games[offset:offset + page_size]

    # Render with current page of games
    return render_template(
        'recommendations.html',
        games=paginated_games,
        next_offset=next_offset,
        previous_offset=previous_offset,
        offset=offset,
        current_platform=platform,
        current_genre=genre,
        age=age,
        name_filter=name_filter,
        show_genre_filter=True
        )

@bp.route('/reset-session', methods=['POST'])
def reset_session():
    session.clear()
    return redirect(url_for('main.index'))