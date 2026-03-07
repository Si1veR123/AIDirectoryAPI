import json
import requests
import websockets
import asyncio

BASE_URL = "http://localhost:8000"
BASE_WS_URL = "ws://localhost:8000"

USERNAME = "superuser"
PASSWORD = "Something123"

QUERY = "ai for analyzing medical images"
TOP_N = 10


def get_token():
    url = f"{BASE_URL}/api/user/token/"
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
    }

    r = requests.post(url, json=payload)
    r.raise_for_status()

    data = r.json()
    return data["access"]


def request_recommendations(token):
    url = f"{BASE_URL}/api/tools/recommend/"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "q": QUERY,
        "top_n": TOP_N
    }

    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()

    data = r.json()

    print("Recommendation request accepted:")
    print(json.dumps(data, indent=2))

    return data["results_url_ws"]


async def wait_for_results(ws_url, token):
    if ws_url.startswith("/"):
        ws_url = BASE_WS_URL + ws_url

    async with websockets.connect(
        ws_url,
        additional_headers={"Authorization": f"Bearer {token}"}
    ) as ws:

        print("\nConnected to websocket. Waiting for results...\n")

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            print("Received message:")
            print(json.dumps(data, indent=2))

            if data.get("type") == "recommendation_ready":
                print("\nRecommendations are ready!")
                break


def main():
    print("Getting JWT token...")
    token = get_token()

    print("Requesting recommendations...")
    ws_url = request_recommendations(token)

    print("Connecting to websocket...")
    asyncio.run(wait_for_results(ws_url, token))

if __name__ == "__main__":
    main()