import streamlit as st
import pandas as pd
import numpy as np
import pickle
from difflib import get_close_matches,SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from surprise import SVD, Dataset, Reader
import matplotlib.pyplot as plt
import re
from wordcloud import WordCloud 
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging


@st.cache_resource
def download_nltk_resources():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download("punkt")
        nltk.download("stopwords")

download_nltk_resources()

# إعداد اللوجر
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')


@st.cache_data
def load_and_preprocess_data():
    with open('Cleaned_df.pkl', 'rb') as f:
        df = pickle.load(f)
    ratings = pd.read_csv("D:\Models\Recommender System\Recommendation System( The Movies )/ratings.csv")
    links = pd.read_csv("D:\Models\Recommender System\Recommendation System( The Movies )/links.csv")

    links.dropna(inplace=True)
    links['tmdbId'] = links['tmdbId'].astype(int)
    ratings = ratings.merge(links[['movieId', 'tmdbId']], on='movieId')
    ratings = ratings.rename(columns={'tmdbId': 'id'})

    return df, ratings


df, ratings = load_and_preprocess_data()


def calc_cosine_sim():
    vec = TfidfVectorizer(stop_words='english')
    Frequency = vec.fit_transform(df['combined_text'])
    sim = cosine_similarity(Frequency)
    with open('movies_similarity.pkl','wb') as f:
        pickle.dump(sim,f)

@st.cache_resource
def load_similarity_matrix():
    try:
        with open('movies_similarity.pkl', 'rb') as f:
            sim = pickle.load(f)
        return sim
    except FileNotFoundError:
        logging.info("Calculating Similarity Matrix for the first time...")
        calc_cosine_sim()
        with open('movies_similarity.pkl', 'rb') as f:
            sim = pickle.load(f) # نستخدم load مش dump
        return sim


def training_calculation(): 
    reader = Reader(rating_scale=(1,5))
    dataset = Dataset.load_from_df(ratings[['userId','id','rating']].sample(1000000), reader)
    trainset = dataset.build_full_trainset()

    svd = SVD(n_factors=50, n_epochs=20) 
    svd.fit(trainset)
    with open('svd_training_calculation.pkl','wb') as f:
        pickle.dump(svd,f)

@st.cache_resource
def load_svd_model():
    try:
        with open('svd_training_calculation.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        logging.info("Training SVD Model for the first time...")
        training_calculation()
        with open('svd_training_calculation.pkl', 'rb') as f:
            svd = pickle.load(f) # نستخدم load مش dump
        return svd


def Recommendation(Movie_name, with_scores=False, top_n=10):
    Movies_list = df["title"].to_list()
    sim = load_similarity_matrix()

    find_close_match = get_close_matches(Movie_name, Movies_list)

    if not find_close_match:
        print(f"Movie '{Movie_name}' not found. Please try another movie!")
        return []

    closest = find_close_match[0]
    similarity_ratio = SequenceMatcher(None, Movie_name.lower(), closest.lower()).ratio()

    if similarity_ratio < 0.7:
        print("Movie not similar enough, please enter another movie!")
        return []

    print(f"Selected Movie: {closest}")

    index_of_the_movie = df[df.title == closest].index[0]
    similarity_score = list(enumerate(sim[index_of_the_movie]))
    sorted_similar_movies = sorted(similarity_score, key=lambda x: x[1], reverse=True)

    suggested_movies = []
    i = 0
    for index, score in sorted_similar_movies:
        title_from_index = df.iloc[index]['title']

        if title_from_index != closest:
            if with_scores:
                suggested_movies.append((title_from_index, score))
            else:
                suggested_movies.append(title_from_index)
            i += 1
        if i >= top_n:
            break

    return suggested_movies


def Collaborative_recommendation(user_id, num_recommendations=10): 
    svd_train = load_svd_model()   
            
    all_movie_ids = set(ratings['id'].unique())
    movies_watched = set(ratings[ratings['userId'] == user_id]['id'].unique())
    movies_to_predict = list(all_movie_ids - movies_watched)
    # 2. الحل السريع: تجهيز بيانات الاختبار وحسابها دفعة واحدة
    # نحتاج لبناء قائمة تحتوي على (user_id, movie_id, rating_placeholder)
    # بيحسب للأفلام اللي إنت حطيتها له في القائمة اللي اسمها movies_to_predict 
    # الموديل بيمسك فيلم فيلم من القائمة دي، ويقول: "لو اليوزر ده شاف الفيلم ده، غالباً هيديله 4.5... والفيلم اللي بعده هيديله 2.1..." وهكذا. 
    testset = [[user_id, m_id, 4.0] for m_id in movies_to_predict]

    # التنبؤ لكل الأفلام في خطوة واحدة
    # svd_train.predict(user_id, m_id) (بينادي الدالة 10,000 مرة)
    predictions_raw = svd_train.test(testset)

    # 3. استخراج النتائج وترتيبها
    # pred.iid هو الـ movieId و pred.est هو التقييم المتوقع
    predictions = [(pred.iid, pred.est) for pred in predictions_raw]
    predictions.sort(key=lambda x: x[1], reverse=True)
        
    top_movies = []
    for m_id, est_score in predictions[:num_recommendations]:
        title_list = df[df['id'] == m_id]['title'].values
        if len(title_list) > 0:
            top_movies.append((title_list[0], est_score))  # <--- رجعنا السكور
    return top_movies

if __name__ == "__main__":
    sim = load_similarity_matrix()    
    model = load_svd_model()