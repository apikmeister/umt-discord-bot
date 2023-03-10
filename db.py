from bson.objectid import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import requests

load_dotenv()
KEY = (os.getenv('ENC_KEY')).encode('utf-8')
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)

LOGIN_URL = (os.getenv('LOGIN_URL'))



users_collection = client.usersinfo.users

def encryptpass(password):
    password=Fernet(KEY).encrypt(password.encode('utf-8'))
    return password

def getUser(discord_id):
    user = users_collection.find_one({"discord_id": discord_id})
    if user is None:
        return False
    user["password"] = (Fernet(KEY).decrypt(user["password"])).decode('utf-8')
    payload = {
        'login': 'student',
        'uid': user["username"],
        'pwd': user["password"] ,
        'submit': 'Log Masuk'
    }
    return payload

def getSession(payload):
    s = requests.Session()
    s.post(LOGIN_URL, data=payload, verify=False, allow_redirects=True)
    return s

def getResponse(payload): 
    response = requests.Session().post(LOGIN_URL, data=payload, verify=False, allow_redirects=True)
    return response

def checkUser(discord_id):
    if getUser(discord_id):
        return True
    else:
        return False
    
def addUser(discord_id ,username, password):
    if not checkUser(username):
        password = encryptpass(password)
        user = { 
                "discord_id": discord_id,
                "username": username,
                "password": password
        }
        users_collection.insert_one(user)
        return True
    
def updatePass(discord_id, username, password):
    if checkUser(discord_id):
        users_collection.update_one(
            {'username': username},
            {"$set":{'password': password}})
        return True
    
def deleteUser(discord_id):
    if checkUser(discord_id):
        users_collection.delete_one({"discord_id": discord_id})
        return True

