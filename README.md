# Stock Picker

A comprehensive stock analysis and screening tool designed for value investing. This application scrapes stock data from multiple countries, calculates financial ratios, and provides insights for investment decisions.

## 🎯 Overview

Stock Picker is a Python-based application that helps investors identify potential value stocks by:
- Scraping stock symbols from multiple countries and regions
- Fetching financial data from Yahoo Finance API
- Calculating key financial ratios for value investing analysis
- Storing data in PostgreSQL for efficient querying and analysis
- Supporting real-time data streaming with Kafka

## 🚀 Features

### Core Functionality
- **Multi-Country Stock Screening**: Supports 40+ countries including US, France, Germany, UK, Japan, and more
- **Financial Ratio Analysis**: Calculates comprehensive financial metrics including:
  - **Valuation Ratios**: P/E, P/S, EV/EBITDA, P/FCF, EV/FCF
  - **Return Metrics**: ROE, ROIC
  - **Liquidity Ratios**: Cash ratio, Current ratio, Quick ratio
  - **Debt Metrics**: Debt-to-equity ratio
  - **Dividend Metrics**: Dividend yield, Payout ratio
  - **Margin Analysis**: Gross, Operating, and Net margins

### Data Pipeline
- **Web Scraping**: Automated stock symbol collection using Selenium
- **API Integration**: Yahoo Finance data fetching
- **Database Storage**: PostgreSQL with structured tables
- **Real-time Processing**: Kafka streaming for live data updates

### Investment Criteria Support
The application is designed around value investing principles:
- P/E ratio: 10-12 (max 20)
- Cash Flow: 5x-7x
- ROE: 7% minimum
- Market cap filtering capabilities

## 🛠️ Technology Stack

- **Python 3.8+**
- **Data Processing**: pandas, numpy
- **Financial Data**: yfinance
- **Web Scraping**: Selenium, ChromeDriver
- **Database**: PostgreSQL
- **Streaming**: Apache Kafka
- **Environment**: Docker (planned)
- **Orchestration**: Apache Airflow (planned)

## 📋 Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Chrome browser (for web scraping)
- Apache Kafka (for streaming features)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock_picker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   DB_DEV_NAME=your_dev_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. **Initialize database**
   ```bash
   python db_dev.py
   ```

## 🚀 Usage

### Basic Stock Screening

1. **Scrape stock symbols**
   ```bash
   python scraper.py
   ```

2. **Process financial data**
   ```bash
   python main.py
   ```

3. **Run streaming pipeline**
   ```bash
   python stream_test.py
   ```

### Configuration Options

The scraper supports various filtering options:
- Market cap ranges (e.g., "300M" to "2B")
- Country/region selection
- Headless mode for server deployment

## 📊 Database Schema

### Core Tables

1. **country**: Country codes and names
2. **stock**: Stock symbols and basic information
3. **financial_ratios**: Comprehensive financial metrics by year

### Sample Queries

```sql
-- Get stocks with P/E ratio between 10-12
SELECT * FROM financial_ratios 
WHERE price_per_earning BETWEEN 10 AND 12;

-- Get stocks with ROE > 7%
SELECT * FROM financial_ratios 
WHERE roe > 7;

-- Get stocks by country and market cap
SELECT * FROM financial_ratios 
WHERE country = 'US' AND market_cap BETWEEN 300000000 AND 2000000000;
```

## 🔄 Data Pipeline

1. **Scraping Phase**: Collect stock symbols from Yahoo Finance screener
2. **Data Fetching**: Retrieve financial statements via yfinance API
3. **Ratio Calculation**: Compute financial ratios for each stock/year
4. **Database Storage**: Store results in PostgreSQL
5. **Streaming**: Real-time updates via Kafka (optional)

## 🏗️ Project Structure

```
stock_picker/
├── main.py              # Main application entry point
├── scraper.py           # Web scraping for stock symbols
├── data_process.py      # Financial ratio calculations
├── db_dev.py           # Database initialization and development
├── db_prod.py          # Production database configuration
├── stream_test.py      # Kafka streaming implementation
├── consumer.py         # Kafka consumer
├── producer.py         # Kafka producer
├── data/               # Data storage directory
├── notes.md            # Project notes and specifications
└── README.md           # This file
```

## 🎯 Investment Strategy

The application is designed for value investing with specific criteria:

### France Fund
- Excludes CAC40 companies
- Focus on smaller, undervalued stocks

### Europe Fund
- Companies under 10B market cap
- Value-oriented screening

### Key Metrics
- **P/E Ratio**: 10-12 (sell if > 20)
- **Cash Flow**: 5x-7x
- **ROE**: Minimum 7%

## 🔮 Future Enhancements

- [ ] Web dashboard with Dash/Plotly
- [ ] Docker containerization
- [ ] Apache Airflow integration
- [ ] Portfolio tracking features
- [ ] Price history analysis
- [ ] Automated trading signals

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes only. It does not constitute financial advice. Always conduct your own research and consult with financial professionals before making investment decisions.

## 📞 Support

For questions or issues, please open an issue on the GitHub repository or contact the development team.