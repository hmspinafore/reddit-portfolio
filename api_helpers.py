import collection_details

import logging
import math

import json

import requests
from requests.models import HTTPError

logger = logging.getLogger("reddit_portfolio_logger")

# https://www.ankr.com/docs/build/products/advanced-api-sdk/nft-methods/
ANKR_URL = "https://rpc.ankr.com/multichain"
HEADERS = {
    "Content-Type": "application/json",
}
PARAMS = {
    "jsonrpc": "2.0",
    "method": "ankr_getNFTsByOwner",
    "params": {
        "blockchain": ["polygon"],
        "walletAddress": "",
        "pageSize": 10,
        "pageToken": "",
        "filter": [
        ],
    },
    "id": 1,
}

REQUEST_ID = 1

# Seems like a good idea to filter, but it causes API to crash sometimes.
#for contract_address in collection_details.CONTRACT_ADDRESS_TO_COLLECTION_SLUG:
#    PARAMS["params"]["filter"].append({ contract_address : [] })

def fetch_token_balance_for_address(address: str, nextPageToken=None) -> list:
    """Fetches data about token balances from ankr's POST URL for given address.
    Returns the JSON response for the given address.

    Raises:
        Exception: If API request fails.
    """
    params = dict(PARAMS)
    params["params"]["walletAddress"] = address
    if nextPageToken is not None:
        params["params"]["pageToken"] = nextPageToken
    global REQUEST_ID
    params["id"] = REQUEST_ID
    REQUEST_ID += 1
    response = requests.post(ANKR_URL, data=json.dumps(params))

    if response.status_code != 200:
        logger.debug(
                f"[Covalent HQ] Failed to fetch token balances from {address}."
                f"Received {response.status_code}: {response.reason}. {response.json()}"
        )
        response.raise_for_status()

    response_json = response.json()
    assets = response_json["result"]["assets"]
    if "nextPageToken" in response_json["result"] and response_json["result"]["nextPageToken"] != "":
        assets.extend(fetch_token_balance_for_address(address, response_json["result"]["nextPageToken"]))
    return assets

def fetch_token_balance_for_multiple_addresses(addresses) -> list:
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

def compute_token_balance_from_json_responses(responses) -> dict:
    """Processes the list of JSON responses about token balances and outputs a dict with
    key = avatar name (str), value = set of token IDs int).
    """
    avatar_to_ids_owned = {}

    for response in responses:
        if response["contractAddress"] not in collection_details.CONTRACT_ADDRESS_TO_COLLECTION_SLUG:
            logger.debug(
                    f"{response['contractAddress']} not a known Reddit Collectible Avatar contract"
                    f"Item response: {response}"
            )
            continue

        nft_name = response["name"]
        avatar_name_raw, avatar_id_str = nft_name.split("#")
        avatar_name, avatar_id = avatar_name_raw.strip(), int(avatar_id_str)
        
        if avatar_name not in avatar_to_ids_owned:
            avatar_to_ids_owned[avatar_name] = set([])

        avatar_to_ids_owned[avatar_name].add(avatar_id)

    return avatar_to_ids_owned
