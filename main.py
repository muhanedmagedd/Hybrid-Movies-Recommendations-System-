import streamlit as st
import requests
import json
from Recommendation import Weighted_Hybrid_Recommendation, df

# 1. إعدادات الصفحة
st.set_page_config(page_title="Movie Recommender", layout="wide")

# --- CSS المحدث ---
st.markdown("""
    <style>
    /* استيراد خطوط حديثة من Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');

    /* 1. الخلفية العامة وتطبيق الخط الجديد */
    .stApp { 
        background-color: #000000; 
        color: white; 
        font-family: 'Poppins', sans-serif; 
    }
    
    /* --- تنسيق شريط التوصيات العلوي --- */
.recommendation-header {
        background: linear-gradient(90deg, #1a1a1a 0%, #000000 100%);
        padding: 14px 22px; /* مساحة متوسطة ومريحة */
        border-radius: 10px;
        border-left: 4.8px solid #e50914; 
        font-family: 'Poppins', sans-serif;
        font-size: 1.0rem; /* حجم متوازن للنص التعريفي */
        margin-bottom: 25px; 
        display: flex;
        align-items: center;
        color: #cccccc;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    .movie-highlight {
        color: #ffffff;
        font-family: 'Bebas Neue', sans-serif; 
        font-size: 1.55rem; /* حجم وسط بين الضخم والصغير */
        margin-left: 15px;
        letter-spacing: 1.5px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }            
            
    header[data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; }
    section[data-testid="stSidebar"] { background-color: #000000 !important; }

    /* ===== Sidebar Labels (User ID, Target Movie, etc.) ===== */
    section[data-testid="stSidebar"] label {
        color: #e6e6e6 !important;
        font-family: 'Poppins', sans-serif !important;
        font-size: 14.5px !important;
        font-weight: 600 !important;
        letter-spacing: 0.4px !important;
        margin-bottom: 6px !important;
    }

    /* النصوص التوضيحية (help text) */
    section[data-testid="stSidebar"] p {
        color: #aaaaaa !important;
        font-size: 12.5px !important;
        font-weight: 400 !important;
    }

    /* إخفاء نص الأيقونة المسرب */
    [data-testid="collapsedControl"] {
        color: transparent !important;
    }
    
    section[data-testid="stSidebar"] svg {
        fill: #dddddd !important;
    }

    /* 3. نصوص المدخلات باللون الأسود */
    section[data-testid="stSidebar"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-family: 'Poppins', sans-serif !important;
    }

    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #000000 !important;
    }
            
    section[data-testid="stSidebar"] hr { 
        margin-top: 5px !important; 
        margin-bottom: 15px !important; 
        border-top: 2px solid #555 !important; 
    }
            
            
    /* 4. تنسيق الزرار */
    div.stButton > button {
        background-color: #e50914 !important;
        border: 1px solid #444 !important;
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 20px !important; 
        padding: 8px 13px !important; 
        border-radius: 8px !important;
    }
            
    div.stButton > button:hover {
        background-color: #ff0a16 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(229, 9, 20, 0.4);
    }
    div.stButton > button p {
        color: white !important;
    }

    /* 5. كروت الأفلام - تم إضافة height ثابت لضمان التناسق */
    .movie-card { 
        background-color: #181818; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 5px; 
        border: 1px solid #333;
        transition: all 0.3s ease;
        height: 280px; /* توحيد الارتفاع */
        overflow: hidden;
    }

    .movie-card:hover {
        transform: translateY(-5px);
        border-color: #e50914;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }

    .imdb-rating { background-color: #f5c518; color: black; padding: 2px 8px; border-radius: 4px; font-weight: 800; }
    .popular-badge { background-color: #e50914; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; margin-left: 10px; font-weight: 600; }
    .text-light-gray { color: #bbbbbb !important; }
    .text-dim-gray { color: #888888 !important; }
    .imdb-link { display: inline-block; margin-top: 10px; padding: 6px 12px; background-color: #333; color: white !important; text-decoration: none; border-radius: 4px; font-size: 0.8rem; }
    .imdb-link:hover { background-color: #e50914; }

    /* 6. Hero Section */
    .hero-container {
        height: 260px;
        background: linear-gradient(90deg, #000000 0%, #440000 100%);
        padding: 60px 40px;
        border-radius: 15px;
        border-left: 8px solid #e50914;
        margin-bottom: 40px;
    }
    .hero-title { font-size: 3rem; font-weight: 800; color: #ffffff; letter-spacing: 2px; }
    .hero-subtitle { font-size: 1.1rem; color: #b3b3b3; max-width: 600px; font-weight: 300; }


    /* --- 7. التعديل الجديد للـ Expander (Storyline) --- */
    [data-testid="stExpander"] {
        background-color: #1a1a1a !important; 
        border-radius: 11px !important;       
        border: 1px solid #333 !important;     
        overflow: hidden;                      
        margin-top: 0px;                     
        margin-bottom: 20px;
    }
    
    [data-testid="stExpander"] summary {
        background-color: #1a1a1a !important;
        color: #e50914 !important;            
        font-weight: 600 !important;
        padding: 10px 15px !important;
    }

    [data-testid="stExpander"] p {
        color: #dddddd !important;
        font-size: 0.9rem !important;
        line-height: 1.6;
    }

    [data-testid="stExpander"] svg {
        fill: #e50914 !important;
    }

    [data-testid="stExpander"] summary:hover {
        background-color: #252525 !important;
        color: #ff0a16 !important;
    }
</style>
    """, unsafe_allow_html=True)


# 2. الدوال المحمية بالكاش
@st.cache_data
def get_movie_list():
    titles = df[df['title'].notna() & ~df['title'].str.startswith('#')]['title'].unique()
    titles_list = [str(t).strip() for t in titles if len(str(t).strip()) > 0]
    return sorted(titles_list, key=lambda x: (not x[0].isalpha(), x.lower()))

@st.cache_data
def cached_movie_detail(title):
    try:
        with open('config.json') as f:
            config = json.load(f)
            api_key = config['OMDB_API_KEY']
        url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}"
        res = requests.get(url).json()
        if res.get("Response") == "True":
            return {
                "plot": res.get("Plot", "N/A"),
                "poster": res.get("Poster", "https://via.placeholder.com/300x450?text=No+Poster"),
                "rating": res.get("imdbRating", "N/A"),
                "year": res.get("Year", "N/A"),
                "genre": res.get("Genre", "N/A"),
                "director": res.get("Director", "N/A"),
                "runtime": res.get("Runtime", "N/A"),
                "imdbID": res.get("imdbID", "")
            }
    except: return None
    return None

# 3. السايدبار
st.sidebar.markdown("""
    <h1 style="text-align: center; color: #e50914; font-weight: 900; font-size: 33px; margin-bottom: 5px;">Control Panel</h1>
    <hr style="border-top: 2px solid #555; margin-top: 0px; margin-bottom: 20px;">
    """, unsafe_allow_html=True)

user_id = st.sidebar.number_input("User ID:", min_value=1, value=1)

# التحكم في عدد الأفلام (Number Input بدل Slider)
top_n = st.sidebar.number_input("Number of Recommendations:", min_value=1, max_value=50, value=10)

movie_titles = get_movie_list()
selected_movie = st.sidebar.selectbox("Target Movie:", movie_titles)

# تغيير المسمى ليكون أوضح للمستخدم العادي
alpha = st.sidebar.slider(
    "Recommendation Focus", 
    0.0, 1.0, 0.8, 
    help="Move left for 'My Personal Taste' | Move right for 'Similar to this Movie'")

st.sidebar.markdown("---")
side_col1, side_col2, side_col3 = st.sidebar.columns([1, 1.45, 1])
with side_col2:
    recommend_button = st.button("Recommend")

# 4. العرض الرئيسي
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">MOVIES<span style="color:#e50914;">FLIX</span></div>
        <div class="hero-subtitle">Unlimited recommendations, movies, and more. Explore the best cinematic matches tailored just for you.</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
    <div class="recommendation-header">
      Recommendations based on: &nbsp; <span class="movie-highlight">{selected_movie}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
    
if recommend_button:
    with st.spinner('Loading...'):
        # 1. بنطلب عدد أكبر شوية (زيادة 10) عشان لو في أفلام ملهاش بيانات نعوضها
        recs = Weighted_Hybrid_Recommendation(user_id=user_id, movie_title=selected_movie, alpha=alpha, top_n=top_n + 40)
    
    if recs:
        # 2. خطوة "الفلترة": بنجيب بيانات الأفلام اللي شغالة بس ونحطها في قائمة
        valid_movies_data = []
        for movie_name in recs:
            if len(valid_movies_data) >= top_n: break # نكتفي بالعدد اللي المستخدم طلبه
            data = cached_movie_detail(movie_name)
            if data and data['poster'] != "N/A": # شرط إن الفيلم يكون له بيانات وصورة
                valid_movies_data.append((movie_name, data))

        # 3. العرض: بنعرض القائمة الجاهزة دي (مستحيل تلاقي فيها خانة فاضية)
        for i in range(0, len(valid_movies_data), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(valid_movies_data):
                    movie_name, data = valid_movies_data[i+j]
                    
                    # (هنا نفس كود الـ HTML والـ CSS بتاعك بدون أي تغيير في الستايل)
                    badge = f'<span class="popular-badge">Popular</span>' if data['rating'] != "N/A" and float(data['rating']) > 7.5 else ""
                    html_content = f"""<div class="movie-card">
<div style="display: flex; gap: 15px; height: 100%;">
<img src="{data['poster']}" style="width: 130px; height: 100%; object-fit: cover; border-radius: 5px;">
<div style="flex: 1; display: flex; flex-direction: column; justify-content: space-between;">
<div>
<h3 style="margin: 0 0 5px 0; color: white; font-weight:600; font-size: 1.1rem; line-height: 1.2;">{movie_name}</h3>
<p class="text-light-gray" style="font-size: 0.85rem; margin-bottom: 5px;">{data['year']} | {data['runtime']}</p>
<div style="margin-bottom: 10px;"><span class="imdb-rating">⭐ {data['rating']}</span>{badge}</div>
<p class="text-light-gray" style="font-size: 0.85rem; margin: 0;"><b>Director:</b> {data['director']}</p>
<p class="text-dim-gray" style="font-size: 0.8rem; margin-top: 5px;">{data['genre']}</p>
</div>
<a href="https://www.imdb.com/title/{data['imdbID']}" target="_blank" class="imdb-link" style="align-self: flex-start;">IMDb Page</a>
</div></div></div>"""
                    
                    with cols[j]:
                        st.markdown(html_content, unsafe_allow_html=True)
                        with st.expander("Read Storyline"):
                            st.write(data['plot'])
    else:
        st.error("No recommendations found.")