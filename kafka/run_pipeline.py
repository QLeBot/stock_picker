#!/usr/bin/env python3
"""
Main script to run the Kafka-based stock scraping pipeline.
This script orchestrates the entire workflow.
"""

import subprocess
import time
import sys
import os
from datetime import datetime
import signal

def check_kafka_running():
    """Check if Kafka is running on localhost:9092."""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 9092))
        sock.close()
        return result == 0
    except:
        return False

def start_kafka():
    """Start Kafka using Docker Compose."""
    print("🚀 Starting Kafka and Zookeeper...")
    try:
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("✅ Kafka started successfully")
        
        # Wait for Kafka to be ready
        print("⏳ Waiting for Kafka to be ready...")
        for i in range(30):  # Wait up to 30 seconds
            if check_kafka_running():
                print("✅ Kafka is ready!")
                return True
            time.sleep(1)
        
        print("❌ Kafka failed to start within 30 seconds")
        return False
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Kafka: {e}")
        return False

def run_consumer(script_name, description):
    """Run a consumer script in a separate process."""
    print(f"🔄 Starting {description}...")
    try:
        process = subprocess.Popen([sys.executable, script_name])
        return process
    except Exception as e:
        print(f"❌ Failed to start {description}: {e}")
        return None

def run_producer():
    """Run the producer to send scraping tasks."""
    print("📤 Starting producer to send scraping tasks...")
    try:
        subprocess.run([sys.executable, "kafka_scraper_producer.py"], check=True)
        print("✅ Producer completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Producer failed: {e}")
        return False

def run_monitor():
    """Run the monitoring script."""
    print("📊 Starting pipeline monitor...")
    try:
        process = subprocess.Popen([sys.executable, "kafka_monitor.py"])
        return process
    except Exception as e:
        print(f"❌ Failed to start monitor: {e}")
        return None

def cleanup(processes):
    """Clean up running processes."""
    print("\n🛑 Shutting down processes...")
    for process in processes:
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

def signal_handler(signum, frame):
    """Handle interrupt signals."""
    print("\n⚠️  Received interrupt signal. Shutting down...")
    sys.exit(0)

def main():
    """Main pipeline orchestration."""
    print("="*60)
    print("STOCK SCRAPING KAFKA PIPELINE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    processes = []
    
    try:
        # Step 1: Start Kafka
        if not check_kafka_running():
            if not start_kafka():
                print("❌ Failed to start Kafka. Exiting.")
                return
        else:
            print("✅ Kafka is already running")
        
        # Step 2: Start consumers
        print("\n" + "="*40)
        print("STARTING CONSUMERS")
        print("="*40)
        
        # Start scraping consumer
        scraping_consumer = run_consumer("kafka_scraper_consumer.py", "scraping consumer")
        if scraping_consumer:
            processes.append(scraping_consumer)
            time.sleep(2)  # Give it time to start
        
        # Start processing consumer
        processing_consumer = run_consumer("kafka_processing_consumer.py", "processing consumer")
        if processing_consumer:
            processes.append(processing_consumer)
            time.sleep(2)  # Give it time to start
        
        # Step 3: Start monitor
        print("\n" + "="*40)
        print("STARTING MONITOR")
        print("="*40)
        
        monitor = run_monitor()
        if monitor:
            processes.append(monitor)
            time.sleep(3)  # Give monitor time to start
        
        # Step 4: Run producer
        print("\n" + "="*40)
        print("RUNNING PRODUCER")
        print("="*40)
        
        if not run_producer():
            print("❌ Producer failed. Shutting down...")
            return
        
        # Step 5: Keep running and monitor
        print("\n" + "="*40)
        print("PIPELINE RUNNING")
        print("="*40)
        print("Pipeline is now running. Press Ctrl+C to stop.")
        print("Monitor output will show progress above.")
        
        # Keep the main process alive
        while True:
            time.sleep(1)
            
            # Check if any processes have died
            for i, process in enumerate(processes):
                if process and process.poll() is not None:
                    print(f"⚠️  Process {i} has stopped unexpectedly")
            
    except KeyboardInterrupt:
        print("\n⚠️  Received interrupt signal")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        cleanup(processes)
        print("✅ Pipeline shutdown complete")

if __name__ == "__main__":
    main() 