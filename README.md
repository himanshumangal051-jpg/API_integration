# API_integration

Python project to fetch live cryptocurrency data using `requests`, parse JSON, and display it in a user-friendly table.

## Features
- Fetches live data from the CoinGecko public API
- Search coins by name or symbol (`--query`)
- Filter results by minimum market cap (`--min-market-cap`)
- Limit result count (`--limit`)
- Error handling for network/API/JSON issues

## Setup
```bash
pip install -r requirements.txt
```

## Usage
```bash
python crypto_tracker.py --query bitcoin --currency usd --limit 3
```

Optional filter example:
```bash
python crypto_tracker.py --query coin --min-market-cap 1000000000 --limit 5
```
