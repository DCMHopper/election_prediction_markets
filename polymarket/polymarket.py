from py_clob_client.client import ClobClient
from datetime import datetime
import json

host: str = "https://clob.polymarket.com/"
key: str = ""
chain_id: int = 137  # Polygon chain ID
client = ClobClient(host, key=key, chain_id=chain_id)

with open("polymarket/api/blue_pred_markets.txt") as f:
    token_list = json.load(f)

print(token_list[4])
print(token_list[4]["state"])
print(token_list[4]["tokens"][0]["outcome"])
az_id = token_list[4]["tokens"][0]["token_id"]
print(client.get_price(az_id, "buy"))

current_data = (
    f"datasets/observed/{datetime.now().strftime('%Y%m%d%H')}_state_preds.csv"
)

with open(current_data, "w", encoding="utf-8") as f:
    f.write("State,Party,Value\n")

    for token in token_list:
        state_code = token["state"]
        yes_value = client.get_price(token["tokens"][0]["token_id"], "buy")["price"]
        no_value = client.get_price(token["tokens"][1]["token_id"], "buy")["price"]
        print(f"{state_code} -- YES: {yes_value} NO: {no_value}")
        f.write(f"{state_code},blue,{yes_value}\n")
