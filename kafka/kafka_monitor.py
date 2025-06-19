from kafka import KafkaConsumer
import json
import time
from datetime import datetime
from collections import defaultdict
import threading

class KafkaMonitor:
    def __init__(self):
        self.stats = defaultdict(lambda: {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'pending': 0,
            'errors': []
        })
        
        # Consumers for different topics
        self.consumers = {}
        self.setup_consumers()
    
    def setup_consumers(self):
        """Setup consumers for monitoring different topics."""
        topics = [
            'stock-scraping-tasks',
            'stock-processing-tasks', 
            'scraping-completion',
            'processing-completion',
            'scraping-errors',
            'processing-errors'
        ]
        
        for topic in topics:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers='localhost:9092',
                auto_offset_reset='latest',
                enable_auto_commit=False,
                group_id=f'monitor-{topic}',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            self.consumers[topic] = consumer
    
    def monitor_topic(self, topic_name):
        """Monitor a specific topic."""
        consumer = self.consumers[topic_name]
        
        try:
            for message in consumer:
                data = message.value
                
                if topic_name == 'stock-scraping-tasks':
                    self.stats['scraping']['total'] += 1
                    self.stats['scraping']['pending'] += 1
                    
                elif topic_name == 'stock-processing-tasks':
                    self.stats['processing']['total'] += 1
                    self.stats['processing']['pending'] += 1
                    
                elif topic_name == 'scraping-completion':
                    self.stats['scraping']['completed'] += 1
                    self.stats['scraping']['pending'] -= 1
                    
                elif topic_name == 'processing-completion':
                    self.stats['processing']['completed'] += 1
                    self.stats['processing']['pending'] -= 1
                    
                elif topic_name == 'scraping-errors':
                    self.stats['scraping']['failed'] += 1
                    self.stats['scraping']['pending'] -= 1
                    self.stats['scraping']['errors'].append({
                        'task_id': data.get('task_id'),
                        'region': data.get('region_code'),
                        'error': data.get('error'),
                        'timestamp': data.get('timestamp')
                    })
                    
                elif topic_name == 'processing-errors':
                    self.stats['processing']['failed'] += 1
                    self.stats['processing']['pending'] -= 1
                    self.stats['processing']['errors'].append({
                        'task_id': data.get('task_id'),
                        'symbol': data.get('symbol'),
                        'error': data.get('error'),
                        'timestamp': data.get('timestamp')
                    })
                    
        except Exception as e:
            print(f"Error monitoring topic {topic_name}: {e}")
    
    def print_stats(self):
        """Print current statistics."""
        while True:
            print("\n" + "="*60)
            print(f"KAFKA PIPELINE STATUS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            
            # Scraping stats
            scraping = self.stats['scraping']
            print(f"\n📊 SCRAPING TASKS:")
            print(f"   Total: {scraping['total']}")
            print(f"   Completed: {scraping['completed']}")
            print(f"   Failed: {scraping['failed']}")
            print(f"   Pending: {scraping['pending']}")
            
            if scraping['errors']:
                print(f"   Recent Errors: {len(scraping['errors'][-3:])}")
                for error in scraping['errors'][-3:]:
                    print(f"     - {error['region']}: {error['error'][:50]}...")
            
            # Processing stats
            processing = self.stats['processing']
            print(f"\n🔧 PROCESSING TASKS:")
            print(f"   Total: {processing['total']}")
            print(f"   Completed: {processing['completed']}")
            print(f"   Failed: {processing['failed']}")
            print(f"   Pending: {processing['pending']}")
            
            if processing['errors']:
                print(f"   Recent Errors: {len(processing['errors'][-3:])}")
                for error in processing['errors'][-3:]:
                    print(f"     - {error['symbol']}: {error['error'][:50]}...")
            
            # Overall progress
            total_tasks = scraping['total'] + processing['total']
            completed_tasks = scraping['completed'] + processing['completed']
            failed_tasks = scraping['failed'] + processing['failed']
            
            if total_tasks > 0:
                progress = (completed_tasks / total_tasks) * 100
                print(f"\n📈 OVERALL PROGRESS:")
                print(f"   Progress: {progress:.1f}% ({completed_tasks}/{total_tasks})")
                print(f"   Success Rate: {(completed_tasks/(completed_tasks+failed_tasks)*100):.1f}%" if (completed_tasks+failed_tasks) > 0 else "   Success Rate: 0%")
            
            print("\n" + "="*60)
            time.sleep(10)  # Update every 10 seconds
    
    def run(self):
        """Start monitoring all topics."""
        print("Starting Kafka pipeline monitor...")
        
        # Start monitoring threads for each topic
        threads = []
        for topic in self.consumers.keys():
            thread = threading.Thread(target=self.monitor_topic, args=(topic,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Start stats printing thread
        stats_thread = threading.Thread(target=self.print_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down monitor...")
            for consumer in self.consumers.values():
                consumer.close()

def main():
    monitor = KafkaMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 