from pymongo import MongoClient

#client = MongoClient("")
#db = client.scheduler

def insert_one(collection, query, doc):
    x = db[collection].insert_one(doc) if not query else db[collection].insertOne(query, doc)
    return x

def find_one(collection, query):
    x = db[collection].find_one(query)
    return x
