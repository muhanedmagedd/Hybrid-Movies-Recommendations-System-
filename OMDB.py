import requests
import json

with open('config.json') as f:
    config = json.load(f)
    API_KEY = config['OMDB_API_KEY']

def Get_Movie_Detail(Movie_Title):
    url = f"http://www.omdbapi.com/?t={Movie_Title}&apikey={API_KEY}"
    res = requests.get(url).json()  # لازم () عشان تتحول لدكشنري
    if res.get("Response") == "True":
        plot = res.get("Plot", "N/A")
        poster = res.get("Poster", "N/A")
        return plot, poster
    return "N/A", "N/A"
