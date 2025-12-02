import time
import random
import requests
import json
import os
from datetime import datetime

# Load settings
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/logs")
INTERVAL = int(os.getenv("INTERVAL", "5"))  # seconds

SERVICES = ["auth-service", "payment-service", "mail-service", "gateway-service"]
LEVELS = ["INFO", "WARNING", "ERROR"]

MESSAGES = {
    "INFO": [
        "Operation completed successfully",
        "Background task executed",
        "User navigation recorded",
        "Status check ok",
    ],
    "WARNING": [
        "User reached rate limit",
        "Slow response detected",
        "Retrying external API",
    ],
    "ERROR": [
        "Login failed for user",
        "Database connection lost",
        "Payment processing error",
        "External API timeout",
        "Unexpected server exception",
    ]
}

def generate_log():
    level = random.choice(LEVELS)
    service = random.choice(SERVICES)
    message = random.choice(MESSAGES[level])

    log = {
        "service": service,
        "level": level,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "meta": {
            "user_id": random.randint(1, 9999),
            "ip": f"192.168.1.{random.randint(2, 254)}",
            "device": random.choice(["android", "ios", "windows", "linux"]),
        }
    }

    return log


def send_log(log):
    try:
        response = requests.post(BACKEND_URL, json=log)
        print(f"[SENT] {log['level']} - {log['service']} - {log['message']}  → Status: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Failed to send log: {e}")


def main():
    print(f"Log generator started → sending logs every {INTERVAL} seconds...")
    while True:
        log = generate_log()
        send_log(log)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
