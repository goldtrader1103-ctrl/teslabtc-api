import os, json

DATA_PATH = "/app/data"
BINANCE_KEYS_FILE = os.path.join(DATA_PATH, "binance_keys.json")
os.makedirs(DATA_PATH, exist_ok=True)

def load_keys() -> dict:
    if not os.path.exists(BINANCE_KEYS_FILE):
        return {}
    with open(BINANCE_KEYS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data if isinstance(data, dict) else {}

def save_keys(data: dict):
    with open(BINANCE_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def set_user_keys(telegram_id: int, api_key: str, api_secret: str):
    data = load_keys()
    data[str(telegram_id)] = {"api_key": api_key, "api_secret": api_secret}
    save_keys(data)

def get_user_keys(telegram_id: int):
    data = load_keys()
    return data.get(str(telegram_id))
