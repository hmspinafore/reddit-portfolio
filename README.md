# Running

  * Run `$ python estimate_portfolio.py [wallet address]` (by default wallet address is r/avatartrading address)
    * Multiple addresses supported! `$ python estimate_portfolio.py [wallet1] [wallet2] ...` 

# Sample output

```bash
$ python estimate_portfolio.py 0x69100a66B28bE3B74D7d5814F31b4DF22Ea421Ee
Token balance found: {'Bloopy McBloopface': {1009}, 'Redd Mummy': {563}, 'April May': {310}, 'Miss Ophelia Surprise': {97}, 'Bow Wow Bandits': {881}, 'Joy Kawaii Cowgirl': {49}, 'Lava Lamp Avatar': {191}}

===================================
Computing subtotals for each avatar
===================================
[Growl Gang x Reddit Collectible Avatars]
	Bow Wow Bandits: 1 * 0.077899 = 0.077899
	[Collection subtotal] = 0.077899
[Drag Queens of Big Gay Baby x Reddit Collectible Avatars]
	April May: 1 * 0.012 = 0.012
	Miss Ophelia Surprise: 1 * 0.027 = 0.027
	[Collection subtotal] = 0.039
[Joy Girls Club x Reddit Collectible Avatars]
	Joy Kawaii Cowgirl: 1 * 0.01345 = 0.01345
	[Collection subtotal] = 0.01345
[Lightspeed Lads x Reddit Collectible Avatars]
	Bloopy McBloopface: 1 * 0.029 = 0.029
	[Collection subtotal] = 0.029
[Peculiar Gang x Reddit Collectible Avatars]
	Redd Mummy: 1 * 0.0343 = 0.0343
	[Collection subtotal] = 0.0343
[Gettin' Groovy x Reddit Collectible Avatars]
	Lava Lamp Avatar: 1 * 0.0375 = 0.0375
	[Collection subtotal] = 0.0375
===================================
Estimated portfolio value in ETH: 0.231149
```
