from django.shortcuts import render, redirect,get_object_or_404
from django.http import FileResponse, HttpResponse , HttpResponseNotFound, JsonResponse
import requests
from movie_recommendation_system.settings import TMDB_HEADER , TMDB_TOKEN ,TMDB_API_KEY 
import time
from functools import wraps

def retry(func):
    """Decorator to retry a function multiple times upon failure."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        delay = 1  # Delay in seconds between retries
        for _ in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error: {e}. Retrying in {delay} seconds...")
                time.sleep(delay)
        raise Exception("Max retries exceeded. Function failed.")
    return wrapper

@retry
def make_api_request(url):
    response = requests.get(url,headers=TMDB_HEADER)
    response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
    return response.json()

def home(request):
    try:
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc" 
        response = make_api_request(url)
        return render(request, 'index.html' , {'movies': response['results']})
    except Exception as e:
        return render(request, 'failedToLoad.html')


def movie(request,id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{id}?language=en-US"
        similar_url = f"https://api.themoviedb.org/3/movie/{id}/similar?language=en-US&page=1"
        response = make_api_request(url)
        similar_response = make_api_request(similar_url)
        return render(request, 'movie.html',{'movie':response,'similar':similar_response['results']})
    except Exception as e:
        print(e)
        return render(request, 'failedToLoad.html')

def search(request):
    try:
        query = request.GET.get('query')
        query1 = query.replace(" ","%")
        url = f"https://api.themoviedb.org/3/search/movie?query={query1}&include_adult=true&language=en-US&page=1"
        response = make_api_request(url)
        return render(request,'search.html',{'movies': response['results'],'query':query})
    except Exception as e:
        return render(request, 'index.html')