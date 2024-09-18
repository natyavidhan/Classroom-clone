from dotenv import load_dotenv
import os

load_dotenv()

config ={
    'FIREBASE_CONFIG': {
        'apiKey': os.getenv('FIREBASE_API_KEY'),
        'authDomain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'databaseURL': os.getenv('FIREBASE_DATABASE_URL'),
        'projectId': os.getenv('FIREBASE_PROJECT_ID'),
        'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messagingSenderId': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'appId': os.getenv('FIREBASE_APP_ID'),
        'measurementId': os.getenv('FIREBASE_MEASUREMENT_ID')
    },
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'GITHUB_CLIENT_ID': os.getenv('GITHUB_CLIENT_ID'),
    'GITHUB_CLIENT_SECRET': os.getenv('GITHUB_CLIENT_SECRET'),
    'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID'),
    'GOOGLE_CLIENT_SECRET': os.getenv('GOOGLE_CLIENT_SECRET'),
    'GITLAB_CLIENT_ID': os.getenv('GITLAB_CLIENT_ID'),
    'GITLAB_CLIENT_SECRET': os.getenv('GITLAB_CLIENT_SECRET'),
    'DISCORD_CLIENT_ID': os.getenv('DISCORD_CLIENT_ID'),
    'DISCORD_CLIENT_SECRET': os.getenv('DISCORD_CLIENT_SECRET'),
    'MONGO_URI': os.getenv('MONGO_URI')
}