import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class GameRecommender:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.games_df = None
        self.reviews_df = None
        self.embeddings = None
        
    def load_data(self):
        """Load and preprocess the game and review data"""
        self.games_df = pd.read_csv('data/processed/games_processed.csv')
        self.reviews_df = pd.read_csv('data/processed/reviews_processed.csv')
        
    def generate_embeddings(self):
        """Generate embeddings for game descriptions"""
        descriptions = self.games_df['description'].fillna('')
        self.embeddings = self.model.encode(descriptions)
        
    def get_recommendations(self, game_id, n_recommendations=5):
        """Get game recommendations based on content similarity"""
        if game_id not in self.games_df['app_id'].values:
            return []
            
        game_idx = self.games_df[self.games_df['app_id'] == game_id].index[0]
        game_embedding = self.embeddings[game_idx].reshape(1, -1)
        
        # Calculate similarity scores
        similarities = cosine_similarity(game_embedding, self.embeddings)[0]
        
        # Get top N similar games (excluding the input game)
        similar_indices = np.argsort(similarities)[::-1][1:n_recommendations+1]
        
        recommendations = self.games_df.iloc[similar_indices][
            ['app_id', 'name', 'description', 'price']
        ].to_dict('records')
        
        return recommendations

# Initialize the recommender
recommender = GameRecommender()

def get_recommendations(game_id):
    """Wrapper function to get recommendations"""
    return recommender.get_recommendations(game_id) 