from pymongo import MongoClient
from uuid import uuid4
import random
import datetime
import requests
import pyrebase

class Database:
    def __init__(self, URL, storage, db):
        self.client = MongoClient(URL)
        self.db = self.client['Classroom-Clone']
        self.users = self.db.users
        self.classes = self.db.classes
        self.resources = self.db.resources
        self.assignments = self.db.assignments

        self.FireDB = db
        self.FireStrg = storage
        
        self.keys = ["A", "B", "C", "D", "E", "F", "G", "H", 
                     "I", "J", "K", "L", "M", "N", "O", "P", 
                     "Q", "R", "S", "T", "U", "V", "W", "X", 
                     "Y", "Z", "0", "1", "2", "3", "4", "5", 
                     "6", "7", "8", "9", "a", "b", "c", "d", 
                     "e", "f", "g", "h", "i", "j", "k", "l", 
                     "m", "n", "o", "p", "q", "r", "s", "t", 
                     "u", "v", "w", "x", "y", "z"]
        
    def addUser(self, email):
        name = requests.get('http://names.drycodes.com/1').json()[0]
        self.users.insert_one({
            '_id': str(uuid4()),
            'username': name,
            'email': email,
            'avatar': f'https://avatars.dicebear.com/api/bottts/{random.randint(100000000000000, 999999999999999999)}.svg',
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p"),
            'classesCreated': [],
            'classesJoined': []
        })
    
    def userExists(self, email):
        return self.users.find_one({'email': email}) is not None
    
    def getUser(self, email):
        return self.users.find_one({'email': email})
    
    def updateName(self, email, name):
        self.users.update_one({'email': email}, {'$set': {'username': name}})
        return True
    
    def getUserWithID(self, ID):
        return self.users.find_one({'_id': ID})
    
    def createClass(self, userID, name, description):
        ID = str(uuid4())
        self.classes.insert_one(
            {
                '_id': ID,
                'by': userID,
                'name': name,
                'description': description,
                'image': f"https://avatars.dicebear.com/api/jdenticon/{random.randint(100000000000000, 999999999999999999)}.svg",
                'created': datetime.datetime.now().strftime(
                    "%d %B %Y, %I:%M:%S %p"
                ),
                'code': ''.join(random.choice(self.keys) for _ in range(8)),
                'members': [userID],
            }
        )

        self.users.update_one({'_id': userID}, {'$push': {'classesCreated': ID}})
        self.users.update_one({'_id': userID}, {'$push': {'classesJoined': ID}})
        
    def getClass(self, ID):
        return self.classes.find_one({'_id': ID})
    
    def addMember(self, classID, userID):
        self.classes.update_one({'_id': classID}, {'$push': {'members': userID}})
        self.users.update_one({'_id': userID}, {'$push': {'classesJoined': classID}})
    
    def removeMember(self, classID, userID):
        self.classes.update_one({'_id': classID}, {'$pull': {'members': userID}})
        self.users.update_one({'_id': userID}, {'$pull': {'classesJoined': classID}})
        
    def getUserClasses(self, userID):
        user = self.getUser(userID)
        print(user)
        return user['classesJoined']
        
    def addResource(self, ID, classID, name, description, link = None):
        self.resources.insert_one({
            '_id': ID,
            'class': classID,
            'name': name,
            'description': description,
            'link': link,
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        })
        
    def getResources(self, classID):
        resources = self.resources.find({'class': classID})
        if resources is None:
            return []
        return list(resources)
    
    def getResource(self, ID):
        return self.resources.find_one({'_id': ID})
    
    def addAssignment(self, classID, name, description, typ):
        self.assignments.insert_one({
            '_id': str(uuid4()),
            'class': classID,
            'name': name,
            'description': description,
            'type': typ,
            'answers': [],
            'created': datetime.datetime.now().strftime("%d %B %Y, %I:%M:%S %p")
        })      
    
    def addAnswer(self, assignmentID, userID, answer):
        self.assignments.update_one({'_id': assignmentID}, {'$push': {'answers': {userID: answer}}})
    
    def getAssignments(self, classID):
        assignments = self.assignments.find({'class': classID})
        if assignments is None:
            return []
        return list(assignments)
    
    def getAssignment(self, assignmentID):
        return self.assignments.find_one({'_id': assignmentID})
        
    def classExists(self, ID):
        return self.classes.find_one({'_id': ID}) is not None
    
    def joinClass(self, userID, code):
        classID = self.classes.find_one({'code': code})
        if classID is None:
            return False
        if userID in classID['members']:
            return False
        self.classes.update_one({'_id': classID['_id']}, {'$push': {'members': userID}})
        self.users.update_one({'_id': userID}, {'$push': {'classesJoined': classID['_id']}})
        return True