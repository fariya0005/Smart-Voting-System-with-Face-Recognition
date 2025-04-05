import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': "smart-voting-demo.appspot.com"
})

folderPath = 'VoterImages'
pathList = os.listdir(folderPath)
imgList = []
voterIds = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    voterIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(f'Voters/{path}')
    blob.upload_from_filename(fileName)

print("Voter IDs:", voterIds)

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding Voter Faces...")
encodeListKnown = findEncodings(imgList)
encodeListWithIds = [encodeListKnown, voterIds]

file = open("VoterEncodings.p", 'wb')
pickle.dump(encodeListWithIds, file)
file.close()
print("Encoding Complete and File Saved")
