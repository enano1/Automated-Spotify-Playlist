import pyrebase

config={
"apiKey": "AIzaSyDMsrURwbp5tIAMjhEvZ3HSTFu06pKS2pQ",
    "authDomain": "final-project-8c911.firebaseapp.com",
    "projectId": "final-project-8c911",
    "storageBucket": "final-project-8c911.appspot.com",
    "messagingSenderId": "341501985016",
    "appId": "1:341501985016:web:1d88322579d6fe66777b0d",
    "measurementId": "G-36YHC3NKXF",
    "databaseURL": ""
}

firebase=pyrebase.initialize_app(config)
auth = firebase.auth()

email = 'test@gmail.com'
password = '123456'

#user = auth.create_user_with_email_and_password(email, password)
#print(user)

user = auth.sign_in_with_email_and_password(email, password)

#info = auth.get_account_info(user['idToken'])
#print(info)

#auth.send_email_verification(user['idToken'])

#auth.send_password_reset_email(email)