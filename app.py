from flask import Flask, session, render_template, request, redirect
import pyrebase


app = Flask(__name__)

config = {
    "apiKey": "AIzaSyDMsrURwbp5tIAMjhEvZ3HSTFu06pKS2pQ",
    "authDomain": "final-project-8c911.firebaseapp.com",
    "projectId": "final-project-8c911",
    "storageBucket": "final-project-8c911.appspot.com",
    "messagingSenderId": "341501985016",
    "appId": "1:341501985016:web:1d88322579d6fe66777b0d",
    "measurementId": "G-36YHC3NKXF",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


app.secret_key = 'secret'
@app.route('/', methods=['POST', 'GET'])
def index():
    if 'user' in session:
        return 'Hi, {}'.format(session['user'])

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            # Assume successful login without checking Firebase for simplicity
            session['user'] = email
            return redirect('/welcome')
        except:
            return 'Failed to login'

    return render_template('home.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            # Assume successful registration without checking Firebase for simplicity
            session['user'] = email
            return redirect('/welcome')
        except:
            return 'Failed to register user'

    return render_template('register.html')

@app.route('/welcome')
def welcome():
    if 'user' in session:
        return render_template('welcome.html', user=session['user'])
    else:
        return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/')

if __name__ == '__main__':
    app.run()
