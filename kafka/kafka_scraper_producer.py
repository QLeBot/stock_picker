from kafka import KafkaProducer
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class StockScrapingProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Wait for all replicas to acknowledge
            retries=3
        )
    
    def send_scraping_task(self, region, market_cap_min="300M", market_cap_max="2B"):
        """Send a scraping task for a specific region to Kafka."""
        task = {
            "task_id": f"scrape_{region['code']}_{int(time.time())}",
            "region_code": region['code'],
            "region_name": region['name'],
            "market_cap_min": market_cap_min,
            "market_cap_max": market_cap_max,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Send to scraping tasks topic
        future = self.producer.send('stock-scraping-tasks', value=task)
        future.add_callback(self.on_send_success).add_errback(self.on_send_error)
        
        print(f"Sent scraping task for {region['name']} ({region['code']})")
        return task["task_id"]
    
    def send_processing_task(self, symbol, name, country_code):
        """Send a stock processing task to Kafka."""
        task = {
            "task_id": f"process_{symbol}_{int(time.time())}",
            "symbol": symbol,
            "name": name,
            "country_code": country_code,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Send to processing tasks topic
        future = self.producer.send('stock-processing-tasks', value=task)
        future.add_callback(self.on_send_success).add_errback(self.on_send_error)
        
        print(f"Sent processing task for {symbol}")
        return task["task_id"]
    
    def on_send_success(self, record_metadata):
        print(f"Message sent successfully to {record_metadata.topic} partition {record_metadata.partition} offset {record_metadata.offset}")
    
    def on_send_error(self, excp):
        print(f"Failed to send message: {excp}")
    
    def close(self):
        self.producer.flush()
        self.producer.close()

def main():
    # Regions to scrape (you can modify this list)
    regions = [
        {"code": "us", "name": "United States"},
        {"code": "fr", "name": "France"},
        {"code": "gb", "name": "United Kingdom"},
        {"code": "de", "name": "Germany"},
        {"code": "jp", "name": "Japan"}
    ]
    
    producer = StockScrapingProducer()
    
    try:
        # Send scraping tasks for each region
        for region in regions:
            producer.send_scraping_task(region)
            time.sleep(1)  # Small delay between sends
        
        print("All scraping tasks sent successfully")
        
    except Exception as e:
        print(f"Error sending tasks: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main() 