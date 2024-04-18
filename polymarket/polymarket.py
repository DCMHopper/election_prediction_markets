from py_clob_client.client import ClobClient

host: str = "https://clob.polymarket.com/"
key: str = ""
chain_id: int = 137 # Polygon chain ID
client = ClobClient(host, key=key, chain_id=chain_id)

next_cursor = ""
try:
    with open('polymarkets.txt', 'w', encoding="utf-8") as f:
        while True:
            resp = client.get_markets(next_cursor=next_cursor)
            for market in resp['data']:
                f.write(f"{market['question']}  +:")
                f.write(f"{market['tokens']}\n")
            next_cursor=resp['next_cursor']
            if next_cursor == 'LTE=' or not next_cursor:
                break
        
except KeyError as e:
    print(f"Key {e} not found in response.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
print("Done.")