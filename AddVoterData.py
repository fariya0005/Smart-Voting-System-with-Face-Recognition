import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://smart-voting-demo.firebaseio.com/"
})

ref = db.reference('Voters')

data = {
    "1001": {
        "name": "Alice Sharma",
        "age": 28,
        "gender": "Female",
        "has_voted": False
    },
    "1002": {
        "name": "Ravi Kumar",
        "age": 33,
        "gender": "Male",
        "has_voted": False
    },
    "1003": {
        "name": "Sneha Singh",
        "age": 24,
        "gender": "Female",
        "has_voted": False
    }
}

for key, value in data.items():
    ref.child(key).set(value)
