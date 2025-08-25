import pymongo

#establishing client connection
client=pymongo.MongoClient("mongodb://localhost:27017/")
print(client)

#creating database
db = client["face_attendance"]

#creating collection

attendance = db["attendance"]
subject = db["subject"]
student = db["student"]

