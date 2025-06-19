from kafka import KafkaConsumer, KafkaProducer
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import yfinance as yf
from data_process import calculate_ratios
import psycopg2
import pandas as pd

load_dotenv()

class StockProcessingConsumer:
    def __init__(self):
        # Consumer for processing tasks
        self.consumer = KafkaConsumer(
            'stock-processing-tasks',
            bootstrap_servers='localhost:9092',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='stock-processor-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        # Producer for sending processed data to database
        self.producer = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all'
        )
        
        # Database connection
        self.db_config = {
            'dbname': os.getenv('DB_DEV_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }
    
    def get_db_connection(self):
        """Create a database connection."""
        return psycopg2.connect(**self.db_config)
    
    def store_ratios_in_db(self, symbol, name, country, ratios_df):
        """Store financial ratios in the database for each year."""
        try:
            conn = self.get_db_connection()
            with conn.cursor() as cur:
                # For each year in the ratios DataFrame
                for _, row in ratios_df.iterrows():
                    # Convert date to datetime if it's not already
                    date = pd.to_datetime(row['Date'])
                    
                    # Insert the data into the database
                    cur.execute("""
                        INSERT INTO financial_ratios (
                            symbol, name, country, sector, industry, market_cap, date, enterprise_value,
                            price_per_share, price_per_earning, enterprise_value_per_ebitda,
                            price_per_free_cash_flow, enterprise_value_per_free_cash_flow,
                            roe, roic, cash_ratio, current_ratio, quick_ratio,
                            debt_to_equity, dividend_yield, payout_ratio,
                            gross_margin, operating_margin, net_margin
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        symbol,
                        name,
                        country,
                        row['Sector'],
                        row['Industry'],
                        row['Market cap'],
                        row['Date'],
                        row['Enterprise value'],
                        row['Price per share'],
                        row['Price per earning'],
                        row['Enterprise value per ebitda'],
                        row['Price per free cash flow'],
                        row['Enterprise value per free cash flow'],
                        row['ROE'],
                        row['ROIC'],
                        row['Cash ratio'],
                        row['Current ratio'],
                        row['Quick ratio'],
                        row['Debt to equity'],
                        row['Dividend yield'],
                        row['Payout ratio'],
                        row['Gross margin'],
                        row['Operating margin'],
                        row['Net margin']
                    ))
                conn.commit()
                print(f"Successfully stored ratios for {symbol} for years {[pd.to_datetime(d).date() for d in ratios_df['Date']]}")
                return True
        except Exception as e:
            print(f"Error storing ratios for {symbol}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def process_stock_task(self, task):
        """Process a stock processing task."""
        try:
            symbol = task['symbol']
            name = task['name']
            country_code = task['country_code']
            
            print(f"Processing stock: {symbol} ({name}) from {country_code}")
            
            # Get financial data and calculate ratios
            ticker = yf.Ticker(symbol)
            
            # Check if ticker is valid
            if ticker.info is None:
                print(f"Ticker {symbol} not found or invalid")
                return
            
            ratios_df = calculate_ratios(ticker)
            
            if not ratios_df.empty:
                # Store ratios in database
                success = self.store_ratios_in_db(symbol, name, country_code, ratios_df)
                
                if success:
                    # Send completion message
                    completion_msg = {
                        "task_id": task['task_id'],
                        "symbol": symbol,
                        "country_code": country_code,
                        "ratios_calculated": len(ratios_df),
                        "timestamp": datetime.now().isoformat(),
                        "status": "completed"
                    }
                    
                    self.producer.send('processing-completion', value=completion_msg)
                    print(f"Completed processing for {symbol}: {len(ratios_df)} years of data")
                else:
                    # Send error message
                    error_msg = {
                        "task_id": task['task_id'],
                        "symbol": symbol,
                        "error": "Failed to store data in database",
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed"
                    }
                    
                    self.producer.send('processing-errors', value=error_msg)
            else:
                print(f"No financial data available for {symbol}")
                
                # Send no-data message
                no_data_msg = {
                    "task_id": task['task_id'],
                    "symbol": symbol,
                    "message": "No financial data available",
                    "timestamp": datetime.now().isoformat(),
                    "status": "no_data"
                }
                
                self.producer.send('processing-completion', value=no_data_msg)
                
        except Exception as e:
            print(f"Error processing stock {task['symbol']}: {e}")
            
            # Send error message
            error_msg = {
                "task_id": task['task_id'],
                "symbol": task['symbol'],
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed"
            }
            
            self.producer.send('processing-errors', value=error_msg)
    
    def run(self):
        """Main consumer loop."""
        print("Starting stock processing consumer...")
        
        try:
            for message in self.consumer:
                task = message.value
                print(f"Received processing task: {task['task_id']}")
                
                # Process the task
                self.process_stock_task(task)
                
        except KeyboardInterrupt:
            print("Shutting down consumer...")
        finally:
            self.consumer.close()
            self.producer.close()

def main():
    consumer = StockProcessingConsumer()
    consumer.run()

if __name__ == "__main__":
    main() 