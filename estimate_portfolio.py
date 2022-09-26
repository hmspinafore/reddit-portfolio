import argparse
import csv

import api_helpers

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


if __name__ == "__main__":
    args = parser.parse_args()
    print(f"Estimating addresses: {args.addresses}")
    print(f"Reading floorprices from: {args.avatar_floorprices_csv}")

    responses = api_helpers.fetch_token_balance_for_multiple_addresses(args.addresses)
    token_balances = api_helpers.compute_token_balance_from_json_responses(args.addresses, responses)
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
    for name in token_balances:
        if name not in name_to_floorprice:
            print(f"====================> Error: {name} not found in floorprice data")
            continue

        count = len(token_balances[name])
        floorprice = name_to_floorprice[name]
        subtotal = count * floorprice
        total += subtotal
        print(f"{name}: {count} * {floorprice} = {subtotal}")

    print("===================================")
    print(f"Estimate portfolio value in ETH: {total}")
