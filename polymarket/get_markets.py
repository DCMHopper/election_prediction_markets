from py_clob_client.client import ClobClient
from time import sleep

host: str = "https://clob.polymarket.com/"
key: str = ""
chain_id: int = 137 # Polygon chain ID
client = ClobClient(host, key=key, chain_id=chain_id)

# This code is what I used to pull the list of markets/tokens from polymarket
# This generates a big ugly .txt that I then filtered and formatted
# Running it on its own is not useful, and should not be used to replace the list of markets

next_cursor = ""
try:
    with open('20240509a_polymarkets.txt', 'w', encoding="utf-8") as f:
        while True:
            sleep(1)
            resp = client.get_markets(next_cursor=next_cursor)
            for market in resp['data']:
                f.write("{+=")
                f.write("    \"state\": +=")
                f.write(f"    \"question\": \"{market['question']}\",+=")
                f.write(f"    \"tokens\": {market['tokens']}+=")
                f.write("}\,\n")
            next_cursor=resp['next_cursor']
            if next_cursor == 'LTE=' or not next_cursor:
                break
        
except KeyError as e:
    print(f"Key {e} not found in response.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
print("Done.")