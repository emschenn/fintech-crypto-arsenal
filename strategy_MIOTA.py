class Strategy():
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, '')

    def __init__(self):
        # strategy property
        self.subscribedBooks = {
            'Bitfinex': {
                'pairs': ['MIOTA-USDT'],
            },
        }
        self.period =  10*60
        self.options = {}

        # user defined class attribute
        self.last_type = 'sell'
        self.last_cross_status = None
        self.close_price_trace = np.array([])
        self.ma_long = 10
        self.ma_short = 5
        self.UP = 1
        self.DOWN = 2
        self.last_price = 0


    """def get_current_ma_cross(self):
        s_ma = talib.SMA(self.close_price_trace, self.ma_short)[-1]
        l_ma = talib.SMA(self.close_price_trace, self.ma_long)[-1]
        if np.isnan(s_ma) or np.isnan(l_ma):
            return None
        if s_ma > l_ma:
            return self.UP
        return self.DOWN"""


    # called every self.period
    def trade(self, information):
        exchange = list(information['candles'])[0]
        pair = list(information['candles'][exchange])[0]
        close_price = information['candles'][exchange][pair][0]['close']
        targetCurrency = pair.split('-')[0] 
        baseCurrency = pair.split('-')[1] 
        Log(f"target: {targetCurrency}")
        Log(f"base: {baseCurrency}")
        Log(f"my money: {self['assets'][exchange][baseCurrency]}")
        if np.size(self.close_price_trace ) == 0:
            self.close_price_trace = np.append(self.close_price_trace, [float(close_price)])
            return [
                    {
                        'exchange': exchange,
                        'amount': -5,
                        'price': -1,
                        'type': 'MARKET',
                        'pair': pair,
                    }
            ]
        baseCurrency_amount = self['assets'][exchange][baseCurrency]
        #ma = self.get_current_ma_cross()
        if baseCurrency_amount < 75000:
            r = 100
            if close_price > self.last_price:
                last_price = close_price
                return [
                            {
                                'exchange': exchange,
                                'amount': -r,
                                'price': -1,
                                'type': 'MARKET',
                                'pair': pair,
                            }
                    ]
        buy_number = 0
        for i in self.close_price_trace:
            if float(close_price) < i:
                buy_number += 1
            else:
                break
        self.close_price_trace = self.close_price_trace[-self.ma_long:]
        self.close_price_trace = np.sort(self.close_price_trace)
        if buy_number == 0:
            return []
        else:
            self.close_price_trace = self.close_price_trace[-buy_number:]
            if baseCurrency_amount > 75000 - (close_price * 1000):
                return [
                        {
                            'exchange': exchange,
                            'amount': buy_number * 1000,
                            'price': -1,
                            'type': 'MARKET',
                            'pair': pair,
                        }
            ]
        return []
        
        

