import requests
import datetime
import re
import json

class Api:
    tickers_url = 'https://netex24.net/api/exchangeDirection/getAll'
    objects_url = 'https://netex24.net/scripts/objects.js'
    currencies = {}
    world_currencies = {}
    tickers = []
    tickers_hum = []
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru,en;q=0.9",
        "cache-control": "max-age=0",
        "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 YaBrowser/22.11.2.807 Yowser/2.5 Safari/537.36'
    }

    def __init__(self):
        self.load_objects()
        self.update_tickers()

    def update_tickers(self):
        response = requests.get(self.tickers_url, headers=self.headers)
        dt = int(datetime.datetime.now().timestamp())
        #print(response.status_code)
        if response.status_code in [200, 201]:
            self.tickers = json.loads(response.content.decode('utf-8'))
        else:
            return -1
        d = []
        dis_l = 0
        for ticker in self.tickers:
            if ticker['isDisabled']:
                dis_l += 1
            else:
                ticker['id'] = self.tickers.index(ticker)
                ticker['timestamp'] = dt
                src_amnt = float(ticker['sourceAmount'])
                trgt_amnt = float(ticker['targetAmount'])
                ticker['targetAmount'] = trgt_amnt / src_amnt
                ticker['sourceAmount'] = 1.0
                d.append(ticker)
                t = ticker
                t['sourceCurrencyName'] = self.get_currency_name(t['sourceCurrencyId'])
                t['sourceCustomerCurrencyName'] = self.get_currency_name(t['sourceCustomerCurrencyId'])
                t['sourceWorldCurrencyName'] = self.get_world_currency_name(t['sourceWorldCurrencyId'])
                t['targetCurrencyName'] = self.get_currency_name(t['targetCurrencyId'])
                t['targetCustomerCurrencyName'] = self.get_currency_name(t['targetCustomerCurrencyId'])
                t['targetWorldCurrencyName'] = self.get_world_currency_name(t['targetWorldCurrencyId'])
                self.tickers_hum.append(t)
        self.tickers = d
        #print(dis_l)
        return 0

    def load_objects(self):
        response = requests.get(self.objects_url, headers=self.headers)
        js = response.content.decode('utf-8').replace('\n',' ').replace('\r','')
        #print(js)
        jso = json.loads(re.findall(r'(?<=currencyNames = ){.*?};',js)[0][:-1])
        self.currencies = jso
        jso = json.loads(re.findall(r'(?<=currencySymbols: ){.*?},', js)[0][:-1])
        self.world_currencies = jso
        jso = json.loads(re.findall(r'(?<=currencyCodes: ){.*?},', js)[0][:-1])
        for j in jso:
            self.world_currencies.update({j:jso[j]})
        self.world_currencies.update({'1009': 'TRX'})
        #print(self.world_currencies)
        #print(self.currencies)

    def get_currency_name(self,id):
        return self.currencies[str(id)]

    def get_world_currency_name(self,id):
        return self.world_currencies[str(id)]

    def get_exchange_load_data(self,id_in,id_out):
        url = f'https://netex24.net/api/exchangeDirection/getBy?source={id_in}&target={id_out}'
        dt = int(datetime.datetime.now().timestamp())
        response = requests.get(url, headers=self.headers)
        js = json.loads(response.content.decode('utf-8'))
        js['timestamp'] = dt
        return js

'''
def prettify(d):
    return json.dumps(d,indent=4,ensure_ascii=False)
'''

if __name__ == '__main__':
    netex = Api()
    for t in netex.tickers_hum:
        print(t)
    #print(prettify(netex.get_exchange_load_data(103,188)))