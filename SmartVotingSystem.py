import cv2
import face_recognition
import pickle
import numpy as np
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://smart-voting-demo.firebaseio.com/",
    'storageBucket': "smart-voting-demo.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

print("Loading Encoded Voter Faces...")
file = open('VoterEncodings.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, voterIds = encodeListKnownWithIds
print("Encodings Loaded")

voted = False
voter_info = {}

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            voter_id = voterIds[matchIndex]
            ref = db.reference(f'Voters/{voter_id}')
            voter_info = ref.get()

            if not voter_info["has_voted"]:
                # Mark vote
                ref.update({
                    'has_voted': True,
                    'voted_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                voted = True
                print(f"\n Vote recorded for {voter_info['name']}")
            else:
                print(f"\n⚠️ {voter_info['name']} has already voted.")

            # Draw bounding box
            y1, x2, y2, x1 = [val * 4 for val in faceLoc]
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0) if not voter_info['has_voted'] else (0, 0, 255), 2)
            cv2.putText(img, voter_info['name'], (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0) if not voter_info['has_voted'] else (0, 0, 255), 2)

    cv2.imshow("Smart Voting System", img)
    key = cv2.waitKey(1)

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
