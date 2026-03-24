import os
import requests


def send_to_pumble(message: str):
    webhook_url = os.getenv("PUMBLE_WEBHOOK_URL")
    if not webhook_url:
        print("[notifier] No webhook URL set — printing to console instead.\n")
        print(message)
        return

    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 200:
        print("[notifier] Message sent successfully.")
    else:
        print(f"[notifier] Failed to send: {response.status_code} {response.text}")
