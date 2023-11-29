import os
import pathlib

import requests
from flask import Flask, session, abort, redirect, request, render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

from dotenv import load_dotenv
load_dotenv()  
# hi hi``

app = Flask("Google Login App")
app.secret_key = os.environ.get("SECRET_KEY") # make sure this matches with that's in client_secret.json
print(app.secret_key)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

GOOGLE_CLIENT_ID = "341501985016-cneblrth1bp5gmda83jrvoaf1vn8cdkp.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID") 
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_SECRET_ID") 
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:5000/spotify_callback"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return "Hello World <a href='/login'><button>Login</button></a>"


@app.route("/protected_area")
@login_is_required
def protected_area():
    user_name = session.get('name', 'Guest')  # Default to 'Guest' if name is not in session
    return render_template('welcome.html', user_name=user_name)


@app.route("/spotify_login")
def spotify_login():
    scope = "user-read-private"  # Add or modify scopes as needed
    auth_url = f"{SPOTIFY_AUTH_URL}?response_type=code&client_id={SPOTIFY_CLIENT_ID}&scope={scope}&redirect_uri={SPOTIFY_REDIRECT_URI}"
    return redirect(auth_url)

# Add a new route for Spotify Callback
@app.route("/spotify_callback")
def spotify_callback():
    code = request.args.get('code')
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=token_data)
    token_info = response.json()
    # Store Spotify token in session or handle it as needed
    session["spotify_token"] = token_info.get('access_token')
    return redirect("/protected_area")

@app.route('/spotify_test', methods=['GET', 'POST'])
def spotify_test():
    if request.method == 'POST':
        # Extract the text input from the form
        text_input = request.form['text_input']
        results = parse_sentence(text_input)    
        for result in results:
            print(result['name'], " ", result['artists'][0]['name'])
            
        # Redirect or render a template after processing
        return redirect("/protected_area")  # Redirect to some other page or

    # If it's a GET request, just render the form page
    return render_template("/protected_area")

def parse_sentence(input):
    sentence = input.split()
    spotify_token = session.get("spotify_token")
    print(sentence)
    results = []
    for word in sentence:
        search_result = search_spotify(word, spotify_token)
        
        if search_result['tracks'] and search_result['tracks']['items']:
            closest_result = search_result['tracks']['items'][0]
            for track in search_result['tracks']['items']:
                "hello"
            print(search_result['tracks']['items'][0]['name'])
            results.append(search_result['tracks']['items'][0])
            
        else:
            return None
    return results

def search_spotify(query, token):
    search_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    params = {
        'q': query,
        'type': 'track',  # or 'artist', 'album', 'playlist'
        'limit': 20  # number of results to return
    }
    response = requests.get(search_url, headers=headers, params=params)
    return response.json()

if __name__ == '__main__':
    app.run()
