
import os       # Used to access environment variables for application configuration
import pathlib  # Ensures compatibility across different operating systems
import math

# Enables HTTP requests to external APIs, essential for interactions with Google and Spotify
import requests
from flask import Flask, session, abort, redirect, request, render_template
from google.oauth2 import id_token              # Verifies Google ID tokens to authenticate users securely
from google_auth_oauthlib.flow import Flow      # managing authentication and token exchange
from pip._vendor import cachecontrol            # Adds caching to HTTP sessions
import google.auth.transport.requests

# for encoding/decoding (handling img data)
import base64

# load environment variables from .env file for secure configuration
from dotenv import load_dotenv
load_dotenv()


app = Flask("Google Login App")
app.secret_key = os.environ.get("SECRET_KEY") # make sure this matches with that's in client_secret.json
print(app.secret_key)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

GOOGLE_CLIENT_ID = "341501985016-cneblrth1bp5gmda83jrvoaf1vn8cdkp.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")     # Define path to client secrets file

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID") 
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_SECRET_ID") 
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:5000/spotify_callback"     # Set redirect URI for Spotify callback
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# Flow object is useful for verifying identity of the users to ensure interactions are secure and trusted
# and handles of users to access specific information from their Google account
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

# Ensures that a user is authenticated before allowing access to certain routes
def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    # asks Google to create a special URL leading to Google's login page (unique and secure)
    authorization_url, state = flow.authorization_url()
    # saved in your app's memory (make sure login process not tampered with)
    session["state"] = state
    return redirect(authorization_url)


# Securely handling user authentication and setting up the user's session
@app.route("/callback")
def callback():
    # exchanges the authorization code for access tokens
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State mismatch, potential CSRF (Cross-Site Request Forgery) attack

    # retrieves the user's profile information using access tokens
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    # stores the user's Google ID and name
    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    
    # redirects to a protected area of the app
    return redirect("/protected_area")


# clears the user's session and redirect the user back to home page
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# (@app.route) is route decorator to assign functions to handle specific routes
@app.route("/")
def index():
    return render_template('home.html')

@app.route("/register")
def register():
    return render_template('register.html')


@app.route("/protected_area")
@login_is_required      # Apply login required decorator
def protected_area():
    user_name = session.get('name', 'Guest')  # Default to 'Guest' if name is not in session
    return render_template('step1.html', user_name=user_name)

@app.route("/protected_area2")
def protected_area():
    user_name = session.get('name', 'Guest')
    return render_template('step2.html', user_name=user_name)

@app.route("/protected_area_success")
def protected_area_success():
    user_name = session.get('name', 'Guest')  # Default to 'Guest' if name is not in session
    spotify_link = session.get('spotify_link', '')
    return render_template('success.html', user_name=user_name, spotify_link=spotify_link)


@app.route("/spotify_login")
def spotify_login():
    scope = "user-read-private playlist-modify-public playlist-modify-private ugc-image-upload"  # Add or modify scopes as needed
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

    access_token = token_info.get('access_token')
    session["spotify_token"] = access_token

    # Get user profile information to retrieve Spotify user ID
    if access_token:
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        user_profile_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
        user_profile_info = user_profile_response.json()

        session["spotify_user_id"] = user_profile_info.get('id')


    # Store Spotify token in session or handle it as needed
    session["spotify_token"] = token_info.get('access_token')
    return redirect("/protected_area2")

@app.route('/spotify_test', methods=['GET', 'POST'])
def spotify_test():
    if request.method == 'POST':
        # Extract the text input from the form
        text_input = request.form['text_input']
        results = parse_sentence(text_input)    
        for result in results:
            print(result['name'], " ", result['artists'][0]['name'])

        spotify_token = session.get("spotify_token")
        playlist = create_playlist("Spotify Playlist", spotify_token)
        print(playlist)
        if playlist is not None:
            playlist_id = playlist['id']
            
        print(playlist_id)

        results_ids = []
        for song in results:
            results_ids.append(song['uri'])
        

        add_songs(playlist_id, results_ids, spotify_token)
        create_playlist_cover(playlist_id, spotify_token)

        # Redirect or render a template after processing

        spotify_link = f"https://open.spotify.com/embed/playlist/{playlist_id}?utm_source=generator"
        session['spotify_link'] = spotify_link

        return redirect("/protected_area_success")  # Redirect to some other page or

    # If it's a GET request, just render the form page
    return render_template("/protected_area")

def create_playlist_cover(playlist_id, spotify_token):
    # Assume you have a playlist ID to use
    playlist_id = playlist_id

    # Fetch and process the dog image
    dog_image_url = fetch_random_dog_image()
    base64_image = download_and_convert_image(dog_image_url)
    
    # Upload to Spotify
    spotify_token = spotify_token
    upload_playlist_cover(playlist_id, base64_image, spotify_token)

    return "Playlist cover updated!"

def fetch_random_dog_image():
    response = requests.get('https://dog.ceo/api/breeds/image/random')

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
       
        # Validate if the 'message' key with the image URL is present
        if 'message' in data and data['message'].startswith('http'):
            return data['message']
        else:
            print("Invalid content received from Dog CEO API")
            return None
    else:
        print(f"Failed to fetch from Dog CEO API. Status code: {response.status_code}")
        return None

def download_and_convert_image(image_url):
    response = requests.get(image_url)

    # Check if the request was successful
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    else:
        print(f"Failed to fetch image. Status code: {response.status_code}")
        return None

def upload_playlist_cover(playlist_id, image_data, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "image/jpeg"
    }
    response = requests.put(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/images',
        headers=headers,
        data=image_data
    )


def add_songs(playlist_id, track_uris, spotify_token):
    """
    Adds songs to a Spotify playlist.

    Parameters:
    playlist_id (str): The Spotify ID of the playlist to add songs to.
    track_uris (list of str): A list of Spotify track URIs to add to the playlist.
    spotify_token (str): Spotify Authorization token.

    Returns:
    response: The response object from the Spotify API request.
    """
    
    # Endpoint URL for adding tracks to a playlist
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    

    # Headers for the POST request, including the authorization token
    headers = {
        "Authorization": f"Bearer {spotify_token}",
        "Content-Type": "application/json"
    }

    # JSON data with the track URIs
    data = {"uris": track_uris}

    # Sending POST request to the Spotify API
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    print(response.json())

    return response

def create_playlist(playlist_name, spotify_token):
    # Spotify API endpoint for creating a playlist
    user_id = session["spotify_user_id"]
    url = f'https://api.spotify.com/v1/users/{user_id}/playlists'
    
    # Headers for the POST request, including the authorization token
    headers = {
        "Authorization": f"Bearer {spotify_token}",
        "Content-Type": "application/json"
    }

    # JSON data with the playlist name
    data = {
        "name": playlist_name,
        "description": "Created with Python",
        "public": True  # Set to True if you want the playlist to be public
    }

    # Sending POST request to the Spotify API
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    print(response.json())

    # Check if the request was successful
    if response.status_code == 201:
        return response.json()  # Returns the created playlist details as JSON
    else:
        return None  
    

def parse_sentence(input):
    sentence = input.split()
    spotify_token = session.get("spotify_token")
    print(sentence)
    results = []
    for word in sentence:
        search_result = search_spotify(word, spotify_token)

        if search_result['tracks'] and search_result['tracks']['items']:
            closest_result = search_result['tracks']['items'][0]
            closest_score = math.inf
            for track in search_result['tracks']['items']:
                track_string = track['name']
                similarity = compare_similarity(word, track_string)
                if similarity < closest_score:
                    closest_result = track
                    closest_score = similarity
                print(track_string, similarity)
                if similarity == 0:
                    break
            print()
            results.append(closest_result)
            
        else:
            continue
    return results

def compare_similarity(s1, s2):
    """compares the similarity of two strings (Levenshtein difference)"""
    # Code from https://www.educative.io/answers/the-levenshtein-distance-algorithm
    a = s1.lower()
    b = s2.lower()
    

    # Declaring array 'D' with rows = len(a) + 1 and columns = len(b) + 1:
    D = [[0 for i in range(len(b) + 1)] for j in range(len(a) + 1)]
    # Initialising first row:
    for i in range(len(a) + 1):
        D[i][0] = i
    # Initialising first column:
    for j in range(len(b) + 1):
        D[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                D[i][j] = D[i - 1][j - 1]
            else:
                # Adding 1 to account for the cost of operation
                insertion = 1 + D[i][j - 1]
                deletion = 1 + D[i - 1][j]
                replacement = 1 + D[i - 1][j - 1]

                # Choosing the best option:
                D[i][j] = min(insertion, deletion, replacement)

    return D[len(a)][len(b)]


def search_spotify(query, token):
    search_url = 'https://api.spotify.com/v1/search'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    refined_query = f'"{query}"'

    params = {
        'q': refined_query,
        'type': 'track',
        'limit': 50  # number of results to return
    }
    response = requests.get(search_url, headers=headers, params=params)
    return response.json()

if __name__ == '__main__':
    app.run()
