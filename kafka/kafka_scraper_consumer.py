from kafka import KafkaConsumer, KafkaProducer
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from scraper import scrape_stocks, save_tickers_to_db
import threading

load_dotenv()

class StockScrapingConsumer:
    def __init__(self):
        # Consumer for scraping tasks
        self.consumer = KafkaConsumer(
            'stock-scraping-tasks',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='stock-scraper-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        # Producer for sending scraped data to processing
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all'
        )
        
        # Producer for sending processing tasks
        self.processing_producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all'
        )
    
    def process_scraping_task(self, task):
        """Process a scraping task for a specific region."""
        try:
            print(f"Processing scraping task for {task['region_name']} ({task['region_code']})")
            
            # Create a single region list for the scraper
            region = {
                "code": task['region_code'],
                "name": task['region_name']
            }
            
            # Run the scraper for this region
            results = scrape_stocks(
                market_cap_min=task['market_cap_min'],
                market_cap_max=task['market_cap_max'],
                regions=[region],
                headless=True  # Run headless for production
            )
            
            # Extract tickers from results
            tickers = results.get(task['region_code'], {})
            
            if tickers:
                # Send each ticker to processing queue
                for name, url in tickers.items():
                    symbol = url.split('/')[-2]
                    
                    # Send to processing tasks topic
                    processing_task = {
                        "task_id": f"process_{symbol}_{int(time.time())}",
                        "symbol": symbol,
                        "name": name,
                        "country_code": task['region_code'],
                        "timestamp": datetime.now().isoformat(),
                        "status": "pending"
                    }
                    
                    self.processing_producer.send('stock-processing-tasks', value=processing_task)
                    print(f"Sent processing task for {symbol}")
                
                # Send completion message
                completion_msg = {
                    "task_id": task['task_id'],
                    "region_code": task['region_code'],
                    "tickers_found": len(tickers),
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed"
                }
                
                self.producer.send('scraping-completion', value=completion_msg)
                print(f"Completed scraping for {task['region_name']}: {len(tickers)} tickers found")
            
            else:
                print(f"No tickers found for {task['region_name']}")
                
        except Exception as e:
            print(f"Error processing scraping task for {task['region_code']}: {e}")
            
            # Send error message
            error_msg = {
                "task_id": task['task_id'],
                "region_code": task['region_code'],
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }
            
            self.producer.send('scraping-errors', value=error_msg)
    
    def run(self):
        """Main consumer loop."""
        print("Starting stock scraping consumer...")
        
        try:
            for message in self.consumer:
                task = message.value
                print(f"Received scraping task: {task['task_id']}")
                
                # Process the task
                self.process_scraping_task(task)
                
        except KeyboardInterrupt:
            print("Shutting down consumer...")
        finally:
            self.consumer.close()
            self.producer.close()
            self.processing_producer.close()

def main():
    consumer = StockScrapingConsumer()
    consumer.run()

if __name__ == "__main__":
    main() 