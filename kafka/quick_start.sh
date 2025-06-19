#!/bin/bash

echo "🚀 Stock Scraping Kafka Pipeline - Quick Start"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create one with your database configuration:"
    echo "DB_DEV_NAME=your_database_name"
    echo "DB_USER=your_username"
    echo "DB_PASSWORD=your_password"
    echo "DB_HOST=localhost"
    echo "DB_PORT=5432"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install kafka-python psycopg2-binary pandas yfinance selenium python-dotenv

# Start Kafka
echo "🚀 Starting Kafka and Zookeeper..."
docker-compose up -d

# Wait for Kafka to be ready
echo "⏳ Waiting for Kafka to be ready..."
for i in {1..30}; do
    if nc -z localhost 9092 2>/dev/null; then
        echo "✅ Kafka is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Kafka failed to start within 30 seconds"
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 Setup complete! You can now:"
echo ""
echo "1. Run the full pipeline:"
echo "   python run_pipeline.py"
echo ""
echo "2. Or run components separately:"
echo "   Terminal 1: python kafka_scraper_consumer.py"
echo "   Terminal 2: python kafka_processing_consumer.py"
echo "   Terminal 3: python kafka_monitor.py"
echo "   Terminal 4: python kafka_scraper_producer.py"
echo ""
echo "3. Monitor Kafka topics at: http://localhost:8080"
echo ""
echo "Press any key to run the full pipeline now..."
read -n 1 -s

# Run the pipeline
python kafka/run_pipeline.py