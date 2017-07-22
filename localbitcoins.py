from lbcapi import api
import urlparse
import pprint

def pretty(something):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(something)

class LocalBitcoins:
    def __init__(self, hmac_key, hmac_secret, usr_name):
        self.hmac_key = hmac_key
        self.hmac_secret = hmac_secret
        self.conn = api.hmac(hmac_key, hmac_secret)
        self.usr_name = usr_name

    def get_income(self, contact_list):
        res = 0.0
        contact_list = contact_list['data']['contact_list']
        for contact in contact_list:
            data = contact['data']
            buyer = data['buyer']['name']
            if (data['released_at'] is not None):
                if (buyer[0:7] != u'volzkzg'):
                    res += float(data['amount'])
        return res

    def get_outcome(self, contact_list):
        sum = 0.0
        contact_list = contact_list['data']['contact_list']
        for contact in contact_list:
            data = contact['data']
            buyer = data['buyer']['name']
            if (data['released_at'] is not None):
                if (buyer[0:7] == u'volzkzg'):
                    sum += float(data['amount'])
        return sum

    def get_profit(self):
        income = 0
        outcome = 0

        contact_list = self.conn.call('GET', '/api/dashboard/closed/').json()
        income += self.get_income(contact_list)
        outcome += self.get_outcome(contact_list)
        while True:
            if ('pagination' not in contact_list):
                break
            if ('next' not in contact_list['pagination']):
                break

            parsed = urlparse.urlparse(contact_list['pagination']['next'])
            params = urlparse.parse_qs(parsed.query)
            contact_list = self.conn.call('GET', '/api/dashboard/closed/', params=params).json()
            # print(params)
            # pretty(contact_list)
            income += self.get_income(contact_list)
            outcome += self.get_outcome(contact_list)

        market_value = self.get_balance() * self.get_current_market_price()
        net_income = income + market_value - outcome
        print("income: {0}".format(income))
        print("outcome: {0}".format(outcome))
        print("market value: {0}".format(market_value))
        print("net income: {0}".format(net_income))

    def get_current_market_price(self):
        tmp = self.conn.call('GET', '/buy-bitcoins-online/CNY/.json').json()
        return float(tmp['data']['ad_list'][0]['data']['temp_price'])

    def get_balance(self):
        tmp = self.conn.call('GET', '/api/wallet/').json()
        return float(tmp['data']['total']['balance'])

    def test(self):
        ads_json = self.conn.call('GET', '/api/dashboard/closed/').json()
        pretty(ads_json)
        parsed = urlparse.urlparse(ads_json['pagination']['next'])
        params = urlparse.parse_qs(parsed.query)
        ads_json_II = self.conn.call('GET', '/api/dashboard/closed/', params=params).json()
        pretty(ads_json_II)



