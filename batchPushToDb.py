from pymongo.mongo_client import MongoClient

uri = "mongodb+srv://ujjwal:7Fjxdksd8iLh1Vsx@authin.ajsijsi.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)

with open("data.txt", 'r') as file:
    for line in file:
        data = line.split("	")
        for i in range(len(data)):
            data[i] = data[i].replace("\n","")
            data[i] = data[i].strip()
        #print(data)

        db = client['Aloha2K23']['DS']

        jsonData = {
            'name': data[0].title(),
            'roll': data[1].upper(),
            'phone': data[2].replace(" ",""),
            'email': data[3].lower(),
            'section': data[4].upper(),
            'paymentMode': data[5].title(),
            'lastCheckIn': "Not Checked In",
            'entryPoint': "Nil"
        }

        #Run only if required
        #insertQuery = db.insert_one(jsonData)
        #print(f"{data[0].title()} - {insertQuery.inserted_id}")

client.close()