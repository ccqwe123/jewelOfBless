import asyncio
import aiohttp
import json
import random
import time
import os
import uuid
import requests
from loguru import logger
import secrets

# Configuration
API_BASE_URL = "https://gateway-run.bls.dev/api/v1"
HEALTH_URL = "https://gateway-run.bls.dev/health"
HARDWARE_INFO_FILE = "hardwareInfo.json"
TOKEN_FILE = "token.txt"
PING_INTERVAL = 120
RETRY_DELAY = 150
PEER_FILE = "peer.txt"
PEER_ID = None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

def get_formatted_time():
    return time.strftime("[%H:%M:%S]")

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            return file.readline().strip()
    logger.error("Token file not found!")
    return None

def load_peer_id():
    global PEER_ID
    if os.path.exists(PEER_FILE):
        with open(PEER_FILE, "r") as file:
            PEER_ID = file.readline().strip()
    else:
        logger.error("Peer file not found!")
        PEER_ID = None

def generate_hardware_id():
    return secrets.token_hex(32)

async def check_service_health(session):
    try:
        async with session.get(HEALTH_URL, headers=HEADERS) as response:
            data = await response.json()
            if data.get("status") == "ok":
                logger.info(f"{get_formatted_time()} Service health check: OK")
            else:
                logger.warning(f"{get_formatted_time()} Service health check failed: {data}")
    except Exception as e:
        logger.error(f"{get_formatted_time()} Error during service health check: {e}")

async def node_status(session, token):
    try:
        url = f"{API_BASE_URL}/nodes/{PEER_ID}"
        headers = {**HEADERS, "Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        async with session.get(url, headers=headers) as response:
            data = await response.json()
            logger.info(f"✅ Node status: OK")
    except Exception as e:
        logger.error(f"❌ Error during node status check: {e}")


async def fetch_ip_address(session):
    try:
        async with session.get("https://api.ipify.org?format=json", headers=HEADERS) as response:
            data = await response.json()
            return data.get("ip")
    except Exception as e:
        logger.error(f"Failed to fetch IP: {e}")
        return None

async def register_node(session, token):
    try:
        url = f"{API_BASE_URL}/nodes/{PEER_ID}"
        payload = {
            "ipAddress": "192.168.1.1",
            "hardwareId": generate_hardware_id(),
            "extensionVersion": "0.1.7"
        }
        headers = {**HEADERS, "Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            logger.info(f"✅ Node registration completed: {data.get('pubKey')}")
            return data
    except Exception as e:
        logger.error(f"❌ Error registering node: {e}")
        return None

async def start_session(session, token):
    try:
        url = f"{API_BASE_URL}/nodes/{PEER_ID}/start-session"
        logger.info(f"📣 Starting session for peer ID {PEER_ID}, it might take a while...")
        headers = {**HEADERS, "Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        async with session.post(url, headers=headers, json={}) as response:
            data = await response.json()
            logger.info(f"📣 Start session response: {data}")
            return data
    except Exception as e:
        logger.error(f"❌ Failed to start session for peer ID {PEER_ID}: {e}")
        return None

async def ping_node(session, token, ip_address):
    url = f"{API_BASE_URL}/nodes/{PEER_ID}/ping"
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    logger.info(f"✅ Pinging node with IP {ip_address}")
    try:
        async with session.post(url, headers=headers) as response:
            data = await response.json()
            return data
    except Exception as e:
        logger.error(f"Ping error: {e}")
        return None

async def process_node(session, token):
    await check_service_health(session)
    await node_status(session, token)
    ip_address = await fetch_ip_address(session)
    if not ip_address:
        logger.error("Failed to retrieve IP address. Retrying...")
        return
    await register_node(session, token)
    await start_session(session, token)
    while True:
        await ping_node(session, token, ip_address)
        await asyncio.sleep(PING_INTERVAL)

async def main():
    token = load_token()
    load_peer_id()
    if not token or not PEER_ID:
        return
    async with aiohttp.ClientSession() as session:
        await process_node(session, token)

if __name__ == "__main__":
    asyncio.run(main())
