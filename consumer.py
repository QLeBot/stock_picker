from kafka import KafkaConsumer
import psycopg2
import json
import os
import dotenv
dotenv.load_dotenv()

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("DB_DEV_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cursor = conn.cursor()

# Kafka Consumer
consumer = KafkaConsumer(
    'country-data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for msg in consumer:
    record = msg.value
    country = record["country"]
    date = record["date"]
    content = record["content"]

    cursor.execute(
        "INSERT INTO scraped_data (country, date, content) VALUES (%s, %s, %s)",
        (country, date, content)
    )
    conn.commit()
