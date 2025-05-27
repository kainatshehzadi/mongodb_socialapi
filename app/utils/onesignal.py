import httpx
import os
from dotenv import load_dotenv

load_dotenv()

ONESIGNAL_APP_ID = os.getenv("ONESIGNAL_APP_ID")
ONESIGNAL_API_KEY = os.getenv("ONESIGNAL_API_KEY")

async def send_onesignal_notification(user_id: str, heading: str, message: str):
    url = "https://onesignal.com/api/v1/notifications"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {ONESIGNAL_API_KEY}"
    }
    payload = {
        "app_id": ONESIGNAL_APP_ID,
        "include_external_user_ids": [user_id],
        "headings": {"en": heading},
        "contents": {"en": message}
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        response.raise_for_status()  # Raises error for 4xx/5xx
        return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"OneSignal HTTP error: {e}")
    except Exception as e:
        raise Exception(f"OneSignal unexpected error: {e}")
