import collection_details
import config

import logging
import math

import requests
from requests.models import HTTPError

logger = logging.getLogger("reddit_portfolio_logger")

# https://www.covalenthq.com/docs/api/#/0/Get%20token%20balances%20for%20address/USD/137
CHQ_BALANCE_URL = "https://api.covalenthq.com/v1/137/address/{address}/balances_v2/?quote-currency=USD&format=JSON&nft=true&no-nft-fetch=true&key={api_key}"
CHQ_GET_EXTERNAL_DATA = "https://api.covalenthq.com/v1/137/tokens/{contract_address}/nft_metadata/{token_id}/?quote-currency=USD&format=JSON&key={api_key}"

HEADERS = {
    "Content-Type": "application/json",
}

def fetch_external_metadata(contract_address: str, token_id: int) -> dict:
    response = requests.get(CHQ_GET_EXTERNAL_DATA.format(
        contract_address=contract_address, token_id=token_id, api_key=config.chq_api_key))

    if response.status_code != 200:
        logger.debug(
                f"[Covalent HQ] Failed to fetch metadata for {contract_address} token {token_id}."
                f"Received {response.status_code}: {response.reason}. {response.json()}"
        )
        response.raise_for_status()

    return response.json()["data"]["items"]

def fetch_token_balance_for_address(address: str) -> list:
    """Fetches data about token balances from Covalent HQ's GET endpoint for given address.
    Returns the JSON response for the given address.

    Raises:
        Exception: If API request fails.
    """
    response = requests.get(CHQ_BALANCE_URL.format(address=address, api_key=config.chq_api_key))

    if response.status_code != 200:
        logger.debug(
                f"[Covalent HQ] Failed to fetch token balances from {address}."
                f"Received {response.status_code}: {response.reason}. {response.json()}"
        )
        response.raise_for_status()

    return response.json()["data"]["items"]

def fetch_token_balance_for_multiple_addresses(addresses: list[str]) -> list:
    """Fetches data about token balances from Covalent HQ's GET endpoint for multiple addresses.
    Returns the concatentated list of JSON responses for the multiple addresses.

    Raises:
        Exception: If API request fails.
    """
    combined: list[dict] = []
    for address in addresses:
        response = fetch_token_balance_for_address(address)
        combined.extend(response)
    return combined

def compute_token_balance_from_json_responses(addresses: list[str], responses: list[dict]) -> dict:
    """Processes the list of JSON responses about token balances and outputs a dict with
    key = avatar name (str), value = set of token IDs int).
    """
    avatar_to_ids_owned = {}

    portfolio = set([])
    for address in addresses:
        portfolio.add(address.lower())

    for response in responses:
        if response["contract_address"] not in collection_details.CONTRACT_ADDRESS_TO_COLLECTION_SLUG:
            logger.debug(
                    f"{response['contract_address']} not a known Reddit Collectible Avatar contract"
                    f"Item response: {response}"
            )
            continue

        for nft_data in response['nft_data']:
            metadata = fetch_external_metadata(response["contract_address"], int(nft_data["token_id"]))
            if metadata[0]['nft_data'][0]['owner_address'] not in portfolio: continue
            nft_name = metadata[0]['nft_data'][0]['external_data']['name']
            avatar_name_raw, avatar_id_str = [s.strip() for s in nft_name.split("#")]
            avatar_name, avatar_id = avatar_name_raw.strip(), int(avatar_id_str)
            if avatar_name == "Cone Head":
                print("response ==================")
                print(response)
                print()
                print("nft data ==================")
                print(nft_data)
                print()
                print("metdata ==================")
                print(metadata)
                print()
        
            if avatar_name not in avatar_to_ids_owned:
                avatar_to_ids_owned[avatar_name] = set([])

            avatar_to_ids_owned[avatar_name].add(avatar_id)

    return avatar_to_ids_owned
