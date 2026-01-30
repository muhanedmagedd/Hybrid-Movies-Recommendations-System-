import logging
from Code import Recommendation, Collaborative_recommendation, ratings, df, load_similarity_matrix, load_svd_model
import pickle
import streamlit as st

@st.cache_resource
def load_models_safely():
    sim = load_similarity_matrix()
    svd = load_svd_model()

    return sim, svd


sim, svd = load_models_safely()

def Weighted_Hybrid_Recommendation(user_id, movie_title, alpha=0.9, top_n=10):
    # 0️⃣ استخراج أنواع (Genres) الفيلم المختار للمقارنة لاحقاً
    try:
        selected_movie_genres = set(df[df['title'] == movie_title]['genres'].iloc[0].split())
    except:
        selected_movie_genres = set()

    # 1️⃣ content-based (movie, content_score) نحولها dict
    content_recs = Recommendation(movie_title, with_scores=True, top_n=100)
    content_dict = {movie: score for movie, score in content_recs}

    # 2️⃣ collaborative (movie, collab_score)
    if user_id in ratings['userId'].unique():
        collab_recs = Collaborative_recommendation(user_id, num_recommendations=500)
        collab_dict = {movie: score for movie, score in collab_recs}
    else:
        collab_dict = {}

    # 3️⃣ دمج كل الأفلام
    all_movies = set(content_dict.keys()) | set(collab_dict.keys())
    final_scores = {}
    
    for movie in all_movies:
        content_score = content_dict.get(movie, 0)
        collab_score_raw = collab_dict.get(movie, 0)
        
        # تحويل سكور الـ SVD ليكون من (0 لـ 1)
        if collab_score_raw > 0:
            collab_score = (collab_score_raw - 1) / (5 - 1)
        else:
            collab_score = 0

        # حساب السكور المبدئي (نفس منطقك القديم)
        if content_score == 0:
            current_score = collab_score * 0.1 
        else:
            current_score = (alpha * content_score + (1 - alpha) * collab_score)

        try:
            # استخراج أنواع الفيلم الحالي اللي بنقيمه
            current_movie_genres = set(df[df['title'] == movie]['genres'].iloc[0].split())
            # تقاطع المجموعات: هل فيه أنواع مشتركة؟
            common_genres = selected_movie_genres.intersection(current_movie_genres)
            if common_genres:
                # لو فيه أنواع مشتركة، بنزود السكور بنسبة 20%
                genre_modifier = 1.2 
            else:
                # لو مفيش أي نوع مشترك، بنخسف بالسكور الأرض (بنزله 20%)
                genre_modifier = 0.2
        except:
            genre_modifier = 1.0 # لو حصلت مشكلة في الداتا خلي السكور زي ما هو

        final_scores[movie] = current_score * genre_modifier

    sorted_movies = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    
    return [movie for movie, score in sorted_movies[:top_n]]