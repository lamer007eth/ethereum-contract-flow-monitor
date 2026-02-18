import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

ADDRESS = os.getenv("BTC_ADDRESS", "").strip()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
FORWARD_CHANNEL_ID = os.getenv("FORWARD_CHANNEL_ID", "").strip()

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
SEEN_TX_FILE = os.getenv("SEEN_TX_FILE", "seen_txids.txt")

API_URL = f"https://mempool.space/api/address/{ADDRESS}/txs"


def require_env():
    missing = []
    if not ADDRESS:
        missing.append("BTC_ADDRESS")
    if not BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not CHAT_ID:
        missing.append("TELEGRAM_CHAT_ID")
    # forward optional
    if missing:
        raise SystemExit(f"Missing .env variables: {', '.join(missing)}")


def fetch_transactions():
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Failed to fetch transactions: {e}")
        return []


def classify_transaction(tx) -> str:
    # OUT if our address appears in inputs (we spent)
    for vin in tx.get("vin", []):
        prevout = vin.get("prevout") or {}
        if prevout.get("scriptpubkey_address") == ADDRESS:
            return "OUT"
    return "IN"


def calc_amount_btc(tx, direction: str) -> float:
    sats = 0

    if direction == "IN":
        for vout in tx.get("vout", []):
            if vout.get("scriptpubkey_address") == ADDRESS:
                sats += int(vout.get("value", 0))
    else:
        for vin in tx.get("vin", []):
            prevout = vin.get("prevout") or {}
            if prevout.get("scriptpubkey_address") == ADDRESS:
                sats += int(prevout.get("value", 0))

    return sats / 1e8


def format_message(tx) -> str:
    txid = tx.get("txid", "")
    direction = classify_transaction(tx)
    amount = calc_amount_btc(tx, direction)

    if direction == "IN":
        emoji = "⬇️"
        label = "INCOMING transaction"
        delta = f"🟩 +{amount:.8f} BTC"
    else:
        emoji = "⬆️"
        label = "OUTGOING transaction"
        delta = f"🟥 -{amount:.8f} BTC"

    return (
        f"{emoji} {label}\n"
        f"{delta}\n"
        f"Address: {ADDRESS}\n"
        f"🔗 https://mempool.space/tx/{txid}"
    )


def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    targets = [{"chat_id": CHAT_ID, "text": msg}]
    if FORWARD_CHANNEL_ID:
        targets.append({"chat_id": FORWARD_CHANNEL_ID, "text": msg})

    for payload in targets:
        try:
            r = requests.post(url, data=payload, timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"❌ Telegram error: {e}")


def load_seen_txids() -> set[str]:
    if not os.path.exists(SEEN_TX_FILE):
        return set()
    with open(SEEN_TX_FILE, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def append_seen_txid(txid: str):
    with open(SEEN_TX_FILE, "a", encoding="utf-8") as f:
        f.write(txid + "\n")


def bootstrap_seen(txs: list[dict]) -> set[str]:
    # First run: record current txids so we don't spam old history
    txids = {tx.get("txid", "") for tx in txs if tx.get("txid")}
    with open(SEEN_TX_FILE, "w", encoding="utf-8") as f:
        for txid in sorted(txids):
            f.write(txid + "\n")
    return txids


def main():
    require_env()

    txs = fetch_transactions()
    if not txs:
        print("No transactions returned. Exiting.")
        return

    seen = load_seen_txids()
    if not seen:
        seen = bootstrap_seen(txs)
        print("✅ Initialized. Current txids saved. Waiting for new transactions...\n")
    else:
        print("✅ Bot started. Waiting for new transactions...\n")

    while True:
        txs = fetch_transactions()
        for tx in txs:
            txid = tx.get("txid")
            if not txid or txid in seen:
                continue

            msg = format_message(tx)
            print(msg + "\n")
            send_telegram(msg)

            seen.add(txid)
            append_seen_txid(txid)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
