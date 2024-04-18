import requests

def get_market_contracts_yes_price(market_id):
    url = f"https://www.predictit.org/api/marketdata/markets/{market_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        market_data = response.json()
        
        contracts_yes_prices = [
            (contract['name'], contract['bestBuyYesCost'])
            for contract in market_data.get('contracts', [])
            if contract['bestBuyYesCost'] is not None  # Filter out contracts without a "Yes" price
        ]
        
        return contracts_yes_prices
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []
    
market_id = 7456
contracts_yes_prices = get_market_contracts_yes_price(market_id)
for contract, price in contracts_yes_prices:
    print(f"Contract: {contract}, Yes Price: {price}")