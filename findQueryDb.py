import json
from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://ujjwal:7Fjxdksd8iLh1Vsx@authin.ajsijsi.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)

db = client['Aloha2K23']['DS']

def findStudent(roll):
    digits = roll.upper()
    query = {'roll': {'$regex': f'.*{digits}$'}}
    result = db.find_one(query)
    for i in result:
        i = json.dumps(i, default=str)
        return i
        

print(findStudent('07'))


client.close()
