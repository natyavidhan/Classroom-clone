from pymongo import MongoClient
from uuid import uuid4
import random
import datetime
import requests

class Database:
    def __init__(self, URL):
        self.client = MongoClient(URL)
        self.db = self.client['Classroom-Clone']
        self.users = self.db.users
        self.data = self.db.data
        
    def addUser(self, email):
        name = requests.get('http://names.drycodes.com/1').json()[0]
        self.users.insert_one({
            '_id': str(uuid4()),
            'username': name,
            'email': email,
            'avatar': f'https://avatars.dicebear.com/api/bottts/{random.randint(100000000000000, 999999999999999999)}.svg',
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        })
    
    def userExists(self, email):
        return self.users.find_one({'email': email}) is not None
    
    def getUser(self, email):
        return self.users.find_one({'email': email})
    
    def updateName(self, email, name):
        self.users.update_one({'email': email}, {'$set': {'username': name}})
        return True