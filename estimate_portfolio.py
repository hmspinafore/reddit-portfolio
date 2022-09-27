import argparse
import csv

import api_helpers
import collection_details

parser = argparse.ArgumentParser()

parser.add_argument(
    "addresses",
    type=str,
    default=["0xC52932d1D825c52d3b36fe38dEF0D1d2002141c0"],
    nargs="*",
    help="Polygon addresses you want to estimate portfolio value of, separated by spaces",
)

parser.add_argument(
    "--avatar_floorprices_csv",
    dest="avatar_floorprices_csv",
    default="avatar_floorprices.csv",
    help="The filename to read Avatar floorprices from in CSV format."
)

parser.add_argument(
    "--chq_api_key",
    dest="chq_api_key",
    default="",
    help="Covalent API Key from covalenthq.com."
)

if __name__ == "__main__":
    args = parser.parse_args()
    print(f"Estimating addresses: {args.addresses}")
    print(f"Reading floorprices from: {args.avatar_floorprices_csv}")

    responses = api_helpers.fetch_token_balance_for_multiple_addresses(args.addresses, args.chq_api_key)
    token_balances = api_helpers.compute_token_balance_from_json_responses(args.addresses, responses, args.chq_api_key)
    print(f"Token balance found: {token_balances}")
    print()

    print("===================================")
    print("Computing subtotals for each avatar")
    print("===================================")
    name_to_floorprice = {}
    with open(args.avatar_floorprices_csv, "r") as csvfile:
        floorprice_reader = csv.reader(csvfile)
        for name, slug, floorprice in floorprice_reader:
            name_to_floorprice[name] = float(floorprice)

    total = 0.
    for slug in collection_details.SLUG_TO_TIERS:
        tier_found = False
        for tier in collection_details.SLUG_TO_TIERS[slug]:
            if tier in token_balances:
                tier_found = True
                break
        if not tier_found: continue

        print(f"[{collection_details.COLLECTION_SLUG_TO_NAME[slug]}]")
        slug_total = 0.
        for tier in collection_details.SLUG_TO_TIERS[slug]:
            if tier in token_balances:
                if tier not in name_to_floorprice:
                    print(f"====================> Error: {name} not found in floorprice data")
                    continue

                count = len(token_balances[tier])
                floorprice = name_to_floorprice[tier]
                subtotal = count * floorprice
                slug_total += subtotal
                total += subtotal
                print(f"\t{tier}: {count} * {floorprice} = {subtotal}")
        print(f"\t[Collection subtotal] = {slug_total}")

    print("===================================")
    print(f"Estimated portfolio value in ETH: {total}")
