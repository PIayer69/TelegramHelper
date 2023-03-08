import requests
from urllib.parse import urljoin



class Crypto:
    def __init__(self, API: str):
        headers = {
            'Authorization': f'Bearer {API}',
            'Accept-Encoding': 'gzip'
        }
        self.session = requests.Session()
        self.session.headers = headers
        self.URL_BASE = "https://api.coincap.io/v2/assets/"
        self.PATH_DATA = "crypto"
    
    def getCoinPrice(self, coinsName: tuple) -> dict:
        # coin_url = urljoin(self.URL_BASE, coinName)
        r = self.session.get(self.URL_BASE, params={'ids': ",".join(coinsName)})
        coin_data = r.json()
        if 'error' in coin_data.keys():
            raise Exception(f"Coin not found: {coinName}")
        return coin_data
    
    
    
        



if __name__ == "__main__":
    c = Crypto("a3575b30-5f30-4503-9c8b-6ab4d7d7522c")
    data = c.getCoinPrice(('dogecoin',))
    print(data)