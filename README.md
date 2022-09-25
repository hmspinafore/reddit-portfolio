# Requirements

  * Get [reddit avatar floorprice scraper](https://github.com/hmspinafore/reddit-avatar-scraper) from github
  * Get API key from [Covalent HQ](https://www.covalenthq.com/) - free tier works fine
    * You need to enter the API key in `config.py`

# Running

  * Run avatar floorprice scraper and copy `avatar_floorprices.csv` from directory
  * Run `$ python estimate_portfolio.py [wallet address]` (by default wallet address is r/avatartrading address but it is empty right now
    * Multiple addresses supported! `$ python estimate_portfolio.py [wallet1] [wallet2] ...` 

# Sample output

```bash
$ python estimate_portfolio.py <REDACTED>
Estimating addresses: ['<REDACTED>']
Reading floorprices from: avatar_floorprices.csv
Token balance found: {'<AVATAR>': {<IDs} }

===================================
Computing subtotals for each avatar
===================================
<AVATAR>: <COUNT> * <PRICE> = <SUBTOTAL>
e.g., [FAKE]
deadass from ny: 10 * 0.01 = 0.1
===================================
Estimate portfolio value in ETH: <TOTAL>
```
