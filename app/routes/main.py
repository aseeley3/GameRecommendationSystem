"""
Main routes module for the Game Recommendation System.
This module handles all the web routes and API endpoints.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.services.recommender import get_recommendations
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
games_dict = {g['appid']: g for g in games}

with open('data_processing/ids_to_reviews.pkl', 'rb') as f:
    reviews_dict = pickle.load(f)

with open("data_processing/description_fallback_embeddings.pkl", "rb") as f:
    embeddings_dict = pickle.load(f)

def platform_filter(game, platform_filter_list):
    game_platforms = game.get('platforms', '').split(';')
    return any(p in platform_filter_list for p in game_platforms)

def age_filter(game, user_age):
    try:
        required_age = int(game.get('required_age', 0))
    except (ValueError, TypeError):
        required_age = 0

    return user_age >= required_age

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
    platforms = request.args.get('platforms')
    is_adult_user = request.args.get('isAdultUser')

    if platforms or is_adult_user is not None:
        if platforms:
            session['platformFilter'] = platforms

        if is_adult_user is not None:
            session['isAdultUser'] = is_adult_user
            print("inSelectPlat")
            print(session['isAdultUser'])

        # Redirect after saving session to avoid resubmission on refresh
        return redirect(url_for('main.select_favorites'))

    # If no parameters, just render the select platform page
    return render_template('select_platform.html')

@bp.route('/select-favorites', methods=['GET', 'POST'])
def select_favorites():

    if 'selected_games' not in session:
        session['selected_games'] = []

    selected_all = set(int(appid) for appid in session.get('selected_games', []))
    page_size = 20
    total_selected_count = len(selected_all)
    # Sort games

    platform_filter_list = session.get('platformFilter', 'windows;mac;linux').split(';')
    user_is_adult = int(session.get('isAdultUser', 0))
    print("inSelectFavs")
    print(platform_filter_list)

    sorted_games = sorted(
        (game for game in games_dict.values()
        if any(platform in platform_filter_list for platform in game['platforms'].split(';'))
        ),
        key=lambda game: len(reviews_dict.get(game['appid'], [])),
        reverse=True
    )

    name_filter = None
    
    filtered_games = [
    game for game in sorted_games
    if platform_filter(game, platform_filter_list)
    and age_filter(game, user_is_adult)
    ]

    if request.method == 'POST':
        
        name_filter = request.form.get('name', '').lower()
        action = request.form.get('action')
        appid_str = request.form.get('appid')
        try:
            appid = int(appid_str)
        except:
            appid = 0

        print(action)

        if action == 'Search':
            offset = 0
        else:
            offset = int(request.form.get('offset', 0))

        if name_filter:
            filtered_games = [game for game in filtered_games if name_filter in game['name'].lower()]
        # Get the current page's games BEFORE modifying offset
        current_page_game_ids = {game['appid'] for game in filtered_games[offset:offset + page_size]}

        # Then modify offset based on button action
        if action == 'Next →':
            offset += page_size
        elif action == '← Previous':
            offset = max(offset - page_size, 0)

        selected = set(session.get('selected_games', []))

        if action == 'add':
            selected.add(appid)
        elif action == 'remove':
            selected.discard(appid)  # discard avoids KeyError if appid isn't present

        session['selected_games'] = list(selected)

        print("Selected game IDs:", session['selected_games'])
        
        if 'continue' in request.form and len(selected_all) > 4:
            return redirect(url_for('main.recommendations'))
    else:
        name_filter = request.args.get('name', '').lower()
        offset = int(request.args.get('offset', 0))
        if name_filter:
            filtered_games = [game for game in filtered_games if name_filter in game['name'].lower()]

    paginated_games = filtered_games[offset:offset + page_size]
    total_selected_count = len(selected_all)

    next_offset = offset + page_size if offset + page_size < len(filtered_games) else None
    previous_offset = max(offset - page_size, 0) if offset > 0 else None

    return render_template(
        'select_favorites.html',
        games=paginated_games,
        next_offset=next_offset,
        previous_offset=previous_offset,
        offset=offset,
        selected=selected_all,
        total_selected_count=total_selected_count,
        name_filter=name_filter
    )

@bp.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    # Get offset from query parameter (default to 0)
    offset = int(request.args.get('offset', 0))
    page_size = 20

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
    
    platform_filter_list = session.get('platformFilter', 'windows;mac;linux').split(';')
    user_is_adult = int(session.get('isAdultUser', 0))

    selected_games = []
    for game_id, similarity in recommendations:
        game = games_dict.get(game_id)
        if game:
            game_copy = game.copy()
            game_copy['similarity'] = similarity
            selected_games.append(game_copy)

    filtered_games = [
    game for game in selected_games
    if platform_filter(game, platform_filter_list)
    and age_filter(game, user_is_adult)
    ]

    next_offset = offset + page_size if offset + page_size < len(filtered_games) else None
    previous_offset = max(offset - page_size, 0) if offset > 0 else None

    # Paginate games
    paginated_games = filtered_games[offset:offset + page_size]
    print(f"Length of Recommendations {len(filtered_games)}")

    # Render with current page of games
    return render_template(
        'recommendations.html',
        games=paginated_games,
        next_offset=next_offset,
        previous_offset=previous_offset
        )