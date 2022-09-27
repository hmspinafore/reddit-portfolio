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

# https://www.covalenthq.com/docs/api/#/0/Get%20token%20balances%20for%20address/USD/137
CHQ_BALANCE_URL = "https://api.covalenthq.com/v1/137/address/{address}/balances_v2/?quote-currency=USD&format=JSON&nft=true&no-nft-fetch=true&key={api_key}"
CHQ_GET_EXTERNAL_DATA = "https://api.covalenthq.com/v1/137/tokens/{contract_address}/nft_metadata/{token_id}/?quote-currency=USD&format=JSON&key={api_key}"

# https://docs.bitski.com/reference/get-owners
BITSKI_TOKEN_OWNERS = "https://api.bitski.com/v1/owners?chainId=137&contractAddress={contract_address}&tokenId={token_id}&fetchNftMetadata=false"

def fetch_token_owners_bitski(contract_address: str, token_id: int) -> dict:
    response = requests.get(BITSKI_TOKEN_OWNERS.format(
        contract_address=contract_address, token_id=token_id))

    if response.status_code != 200:
        logger.debug(
                f"[Bitski] Failed to fetch metadata for {contract_address} token {token_id}."
                f"Received {response.status_code}: {response.reason}. {response.json()}"
        )
        response.raise_for_status()

    return response.json()["balances"]

def fetch_external_metadata_chq(contract_address: str, token_id: int, chq_api_key: str) -> dict:
    response = requests.get(CHQ_GET_EXTERNAL_DATA.format(
        contract_address=contract_address, token_id=token_id, api_key=chq_api_key))

    if response.status_code != 200:
        logger.debug(
                f"[Covalent HQ] Failed to fetch metadata for {contract_address} token {token_id}."
                f"Received {response.status_code}: {response.reason}. {response.json()}"
        )
        response.raise_for_status()

    return response.json()["data"]["items"]


def fetch_token_balance_for_address_chq(address: str, chq_api_key: str) -> list:
    """Fetches data about token balances from Covalent HQ's GET endpoint for given address.
    Returns the JSON response for the given address.
    Raises:
        Exception: If API request fails.
    """
    response = requests.get(CHQ_BALANCE_URL.format(address=address, api_key=chq_api_key))

    if response.status_code != 200:
        logger.debug(
                f"[Covalent HQ] Failed to fetch token balances from {address}."
                f"Received {response.status_code}: {response.reason}. {response.json()}"
        )
        response.raise_for_status()

    return response.json()["data"]["items"]

def fetch_token_balance_for_address_ankr(address: str, nextPageToken=None) -> list:
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
        assets.extend(fetch_token_balance_for_address_ankr(address, response_json["result"]["nextPageToken"]))
    return assets

def fetch_token_balance_for_multiple_addresses(addresses, chq_api_key=None) -> list:
    """Fetches data about token balances from Covalent HQ's GET endpoint for multiple addresses.
    Returns the concatentated list of JSON responses for the multiple addresses.

    Raises:
        Exception: If API request fails.
    """
    combined: list[dict] = []
    for address in addresses:
        if chq_api_key is None or chq_api_key == "":
            response = fetch_token_balance_for_address_ankr(address)
        else:
            response = fetch_token_balance_for_address_chq(address,chq_api_key)
        combined.extend(response)
    return combined

def compute_token_balance_from_json_responses_ankr(responses) -> dict:
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

def compute_token_balance_from_json_responses_chq(addresses, responses, chq_api_key) -> dict:
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
            metadata = fetch_external_metadata_chq(response["contract_address"], int(nft_data["token_id"]), chq_api_key)
            if metadata[0]['nft_data'][0]['owner_address'] not in portfolio: continue

            token_owners = fetch_token_owners_bitski(response["contract_address"], int(nft_data["token_id"]))
            found_owner = False
            for token_owner in token_owners:
                if token_owner["address"] in portfolio:
                    found_owner = True
                    break
            if not found_owner: continue

            nft_name = metadata[0]['nft_data'][0]['external_data']['name']
            avatar_name_raw, avatar_id_str = [s.strip() for s in nft_name.split("#")]
            avatar_name, avatar_id = avatar_name_raw.strip(), int(avatar_id_str)
        
            if avatar_name not in avatar_to_ids_owned:
                avatar_to_ids_owned[avatar_name] = set([])

            avatar_to_ids_owned[avatar_name].add(avatar_id)

    return avatar_to_ids_owned

def compute_token_balance_from_json_responses(addresses, responses, chq_api_key=None) -> dict:
    if chq_api_key is not None and chq_api_key != "":
        return compute_token_balance_from_json_responses_chq(addresses, responses, chq_api_key)
        
    return compute_token_balance_from_json_responses_ankr(responses)
