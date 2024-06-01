from pymongo import MongoClient
import os

client = MongoClient(os.getenv(''))
db = None

def connect():
    global db
    if db is None:
        db = client[os.getenv('Hackathon_DB')]
        print('Connected to MongoDB')

def get_slack_messages():
    if db is None:
        connect()
    return db['slack_messages']

def get_slack_users():
    if db is None:
        connect()
    return db['slack_users']

if __name__ == "__main__":
    connect()  # Initialize the connection when the script is run
