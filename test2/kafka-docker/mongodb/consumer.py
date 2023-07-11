from kafka import KafkaConsumer
from json import loads
from time import sleep
#Conexion mongo
import pymongo

mongoClient = pymongo.MongoClient('mongodb',27017)
db = mongoClient["exampledb"]
coll = db["departure"]

consumer = KafkaConsumer(
    'topic_test',
    bootstrap_servers=['kafka:9093'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group-id',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)
    

for event in consumer:
    event_data = event.value
    print(event_data)
    #Conexion al server de MongoDB
    x = coll.insert_one(event_data)
    print(x.inserted_id)
