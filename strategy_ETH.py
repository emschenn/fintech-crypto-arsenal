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
            'Binance': {
                'pairs': ['ETH-USDT'],
            },
        }
        # seconds for broker to call trade()
        self.period = 60 * 60 
        self.options = {}

        # user defined class attribute
        self.last_type = 'sell'
        self.last_cross_status = None
        self.close_price_trace = np.array([])
        self.UP = 1
        self.DOWN = 2
        self.last_buy_price = 0
        self.short_win = 12   # 短期EMA平滑天数
        self.long_win  = 26   # 長期EMA平滑天数
        self.macd_win  = 9    # DEA線平滑天数
        self.flag = False


    def get_current_macd(self):
        DIF, DEA, MACD = talib.MACD(self.close_price_trace, self.short_win, self.long_win, self.macd_win)
        x = DIF[-1] - DEA[-1]
        if np.isnan(MACD[-1]) or np.isnan(MACD[-4]):
            return None
        if (x > 0):
            return self.UP
        elif (x < 0):
            return self.DOWN
        return None

    def trade(self, information):
        exchange = list(information['candles'])[0]
        pair = list(information['candles'][exchange])[0]
        close_price = information['candles'][exchange][pair][0]['close']
        price = self.close_price_trace

        # add latest price into trace
        self.close_price_trace = np.append(self.close_price_trace, [float(close_price)])
        # calculate current macd cross status
        cur_cross = self.get_current_macd()
        Log('info: ' + str(information['candles'][exchange][pair][0]['time']) + ', ' + str(information['candles'][exchange][pair][0]['open']) + ', assets' + str(self['assets'][exchange]['ETH']))
        self.flag = False

        if cur_cross is None:
            self.flag = True

        if self.last_cross_status is None:
            self.last_cross_status = cur_cross
            self.flag = True

        if self.flag:
            if close_price > self.last_buy_price * 1.01:
                Log('selling, ' + exchange + ':' + pair)
                return [
                    {
                        'exchange': 'Binance',
                        'pair': 'ETH-USDT',
                        'type': 'MARKET',
                        'amount': 20,
                        'price': -1
                    }
                ]
            elif close_price < self.last_buy_price * 0.99:
                self.last_buy_price = close_price
                Log('buying, opt1:' + self['opt1'])
                return [
                    {
                        'exchange': 'Binance',
                        'pair': 'ETH-USDT',
                        'type': 'MARKET',
                        'amount': -20,
                        'price': -1
                    }
                ]

        if self.last_type == 'sell' and \
                cur_cross == self.UP and \
                self.last_cross_status == self.DOWN:
            Log('buying, opt1:' + self['opt1'])
            self.last_type = 'buy'
            self.last_cross_status = cur_cross
            self.last_buy_price = close_price
            return [
                {
                    'exchange': 'Binance',
                    'pair': 'ETH-USDT',
                    'type': 'MARKET',
                    'amount': 20,
                    'price': -1
                }
            ]

        elif  self['assets'][exchange]['ETH'] >0  and \
                self.last_type == 'buy' and \
                cur_cross == self.DOWN and \
                self.last_cross_status == self.UP:
            Log('selling, ' + exchange + ':' + pair)
            self.last_type = 'sell'
            self.last_cross_status = cur_cross
            return [
                {
                    'exchange': 'Binance',
                    'pair': 'ETH-USDT',
                    'type': 'MARKET',
                    'amount': -40,
                    'price': -1
                }
            ]
        else:
            if close_price > self.last_buy_price * 1.01:
                Log('selling, ' + exchange + ':' + pair)
                return [
                    {
                        'exchange': 'Binance',
                        'pair': 'ETH-USDT',
                        'type': 'MARKET',
                        'amount': 20,
                        'price': -1
                    }
                ]
            elif close_price < self.last_buy_price * 0.99:
                self.last_buy_price = close_price
                Log('buying, opt1:' + self['opt1'])
                return [
                    {
                        'exchange': 'Binance',
                        'pair': 'ETH-USDT',
                        'type': 'MARKET',
                        'amount': -20,
                        'price': -1
                    }
                ]

        self.last_cross_status = cur_cross
        return []
