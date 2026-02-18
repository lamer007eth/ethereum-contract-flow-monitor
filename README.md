# Ethereum Contract Flow Monitor 🧠⚡️

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Ethereum](https://img.shields.io/badge/Ethereum-ETH-purple)
![Telegram](https://img.shields.io/badge/Telegram-alerts-2CA5E0)
![Type](https://img.shields.io/badge/Type-Monitoring-purple)
![API](https://img.shields.io/badge/API-REST-grey)

Monitors **buy / sell flows** inside a smart contract (multiple tokens in one contract), tracks known wallets and sends **Telegram alerts** in real time.

---

## ✨ Features

* 🟢 Detects **BUY** transactions
* 🔴 Detects **SELL** transactions (via internal txs)
* 🧠 Decodes contract input data
* 🏷️ Labels known wallets from JSON mapping
* 💰 Calculates token price based on ETH value
* 📊 Estimates Market Cap
* 📩 Sends alerts to multiple Telegram chats
* 🧾 Stores processed tx hashes locally

---

## 📦 Project structure

```text
ethereum-contract-flow-monitor/
├─ contract_flow_monitor.py
├─ requirements.txt
├─ .env.example
├─ wallets.example.json
├─ .gitignore
└─ README.md
```

---

## 🚀 Quick start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2) Create `.env`

Copy `.env.example` → `.env` and fill:

```env
API_KEY=your_etherscan_api_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=123456789,-1001234567890

CONTRACT_ADDRESS=0x00000000000008882d72efa6cce4b6a40b24c860

CHECK_INTERVAL=10
TX_LIMIT=25
SEEN_TX_FILE=seen_hashes.txt
WALLETS_FILE=wallets.json
```

---

### 3) Add wallet labels (optional)

Copy:

```
wallets.example.json → wallets.json
```

Example:

```json
{
  "0x0000000000000000000000000000000000000003": "Trader_1",
  "0x0000000000000000000000000000000000000004": "Whale_2"
}
```

If file is missing — bot still works, just shows raw addresses.

---

### 4) Run

```bash
python contract_flow_monitor.py
```

---

## 📨 Alert example

```
🟢💎 ПОКУПКА PEPE

Сумма: 3.4200 ETH
От: Lamer
Время: 2026-02-18 14:21:55
Курс PEPE: 0.0042$
Market Cap: 88200000$
Курс ETH: 2600$
Количество: 812.00

https://etherscan.io/tx/0x...
```

---

## 🧊 First run behavior

On first start:

* Current transactions are saved into `seen_hashes.txt`
* Old history is ignored
* Only new trades trigger alerts

---

## 🌐 APIs used

* Etherscan → `txlist`
* Etherscan → `txlistinternal`
* CoinGecko → ETH price

---

## 🛠️ Notes

* `seen_hashes.txt` is local state → should not be committed
* Polling too fast may hit Etherscan rate limits
* Wallet labeling is optional via JSON file

---

## 📡 Use cases

* Smart contract trade monitoring
* Whale wallet tracking
* Token launch surveillance
* Telegram alpha feeds
