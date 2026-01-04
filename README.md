# Binance Futures Trading Bot (Testnet)

A **CLI-based Python trading bot** for **Binance USDT-M Futures Testnet** supporting **market, limit, and advanced order types** with strong **validation, logging, and error handling**.

This project was built as part of the **Junior Python Developer – Crypto Trading Bot** hiring assignment.

---

## Features

### Core Features
- Market orders (BUY / SELL)
- Limit orders (BUY / SELL)
- Binance Futures **Testnet** support
- Uses **official Binance API** (`python-binance`)
- Command-line interface (CLI)
- Input validation (symbol, side, quantity, price)
- Displays order execution status and details

### Bonus Features
- OCO (One-Cancels-the-Other) orders


### Logging & Error Handling
- Logs all API requests and responses
- Logs errors with timestamps
- Output stored in `bot.log`

---

##  Project Structure

```text
project_root/
│
├── src/
│   ├── client.py               # Binance client (Testnet)
│   ├── market_order.py         # Market order logic
│   ├── limit_order.py          # Limit order logic
│   ├── utils/
│   │   ├── logging.py          # Logging configuration
│   │   ├── validators.py       # Input validation
│   │   └── __init__.py
│   ├── advanced/
│   │   ├── oco.py              # OCO order implementation
│   │   └── __init__.py
│   └── __init__.py
├── cli.py                      # CLI entry point
├── bot.log                     # Log file 
├── .gitignore
└── README.md
```

## Installation Instructions

Follow the steps below to install and set up the Binance Futures Trading Bot locally.

---

### 1. Clone the Repository

```bash
git clone https://github.com/udaydevs/uday-binance-bot.git
cd binance-futures-bot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  #Activate the virtual environment
```

### 3. Install Required Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
### 4. Configure Environment Variables

```env
API_KEY = your_testnet_api_key
SECRET_KEY = your_testnet_api_secret
```

### 5. Run

```bash
python cli.py
```
