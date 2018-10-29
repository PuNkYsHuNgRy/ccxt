# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
import base64
import hashlib
import math
import json
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import PermissionDenied
from ccxt.base.errors import AddressPending
from ccxt.base.errors import NotSupported


class buda (Exchange):

    def describe(self):
        return self.deep_extend(super(buda, self).describe(), {
            'id': 'buda',
            'name': 'Buda',
            'countries': ['AR', 'CL', 'CO', 'PE'],
            'rateLimit': 1000,
            'version': 'v2',
            'has': {
                'CORS': False,
                'createDepositAddress': True,
                'fetchClosedOrders': True,
                'fetchCurrencies': True,
                'fetchDepositAddress': True,
                'fetchDeposits': True,
                'fetchFundingFees': True,
                'fetchMyTrades': False,
                'fetchOHLCV': True,
                'fetchOpenOrders': True,
                'fetchOrder': True,
                'fetchOrders': True,
                'fetchTrades': True,
                'fetchWithdrawals': True,
                'withdraw': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/47380619-8a029200-d706-11e8-91e0-8a391fe48de3.jpg',
                'api': 'https://www.buda.com/api',
                'www': 'https://www.buda.com',
                'doc': 'https://api.buda.com',
                'fees': 'https://www.buda.com/comisiones',
            },
            'api': {
                'public': {
                    'get': [
                        'pairs',
                        'markets',
                        'currencies',
                        'markets/{market}',
                        'markets/{market}/ticker',
                        'markets/{market}/volume',
                        'markets/{market}/order_book',
                        'markets/{market}/trades',
                        'currencies/{currency}/fees/deposit',
                        'currencies/{currency}/fees/withdrawal',
                        'tv/history',
                    ],
                    'post': [
                        'markets/{market}/quotations',
                    ],
                },
                'private': {
                    'get': [
                        'balances',
                        'balances/{currency}',
                        'currencies/{currency}/balances',
                        'orders',
                        'orders/{id}',
                        'markets/{market}/orders',
                        'deposits',
                        'currencies/{currency}/deposits',
                        'withdrawals',
                        'currencies/{currency}/withdrawals',
                        'currencies/{currency}/receive_addresses',
                        'currencies/{currency}/receive_addresses/{id}',
                    ],
                    'post': [
                        'markets/{market}/orders',
                        'currencies/{currency}/deposits',
                        'currencies/{currency}/withdrawals',
                        'currencies/{currency}/simulated_withdrawals',
                        'currencies/{currency}/receive_addresses',
                    ],
                    'put': [
                        'orders/{id}',
                    ],
                },
            },
            'timeframes': {
                '1m': '1',
                '5m': '5',
                '30m': '30',
                '1h': '60',
                '2h': '120',
                '1d': 'D',
                '1w': 'W',
            },
            'fees': {
                'trading': {
                    'tierBased': True,
                    'percentage': True,
                    'taker': 0.008,  # 0.8%
                    'maker': 0.004,  # 0.4%
                    'tiers': {
                        'taker': [
                            [0, 0.008],  # 0.8%
                            [2000, 0.007],  # 0.7%
                            [20000, 0.006],  # 0.6%
                            [100000, 0.005],  # 0.5%
                            [500000, 0.004],  # 0.4%
                            [2500000, 0.003],  # 0.3%
                            [12500000, 0.002],  # 0.2%
                        ],
                        'maker': [
                            [0, 0.004],  # 0.4%
                            [2000, 0.0035],  # 0.35%
                            [20000, 0.003],  # 0.3%
                            [100000, 0.0025],  # 0.25%
                            [500000, 0.002],  # 0.2%
                            [2500000, 0.0015],  # 0.15%
                            [12500000, 0.001],  # 0.1%
                        ],
                    },
                },
            },
            'exceptions': {
                'not_authorized': AuthenticationError,  # {message: 'Invalid credentials', code: 'not_authorized'}
                'forbidden': PermissionDenied,  # {message: 'You dont have access to self resource', code: 'forbidden'}
                'invalid_record': ExchangeError,  # {message: 'Validation Failed', code: 'invalid_record', errors: []}
                'not_found': ExchangeError,  # {message: 'Not found', code: 'not_found'}
                'parameter_missing': ExchangeError,  # {message: 'Parameter missing', code: 'parameter_missing'}
                'bad_parameter': ExchangeError,  # {message: 'Bad Parameter format', code: 'bad_parameter'}
            },
        })

    async def fetch_currency_info(self, currency, currencies=None):
        if not currencies:
            response = await self.publicGetCurrencies()
            currencies = response['currencies']
        for i in range(0, len(currencies)):
            currencyInfo = currencies[i]
            if currencyInfo['id'] == currency:
                return currencyInfo
        return None

    async def fetch_markets(self):
        marketsResponse = await self.publicGetMarkets()
        markets = marketsResponse['markets']
        currenciesResponse = await self.publicGetCurrencies()
        currencies = currenciesResponse['currencies']
        result = []
        for i in range(0, len(markets)):
            market = markets[i]
            id = market['id']
            baseId = market['base_currency']
            quoteId = market['quote_currency']
            base = self.common_currency_code(baseId)
            quote = self.common_currency_code(quoteId)
            baseInfo = await self.fetch_currency_info(baseId, currencies)
            quoteInfo = await self.fetch_currency_info(quoteId, currencies)
            symbol = base + '/' + quote
            precision = {
                'amount': baseInfo['input_decimals'],
                'price': quoteInfo['input_decimals'],
            }
            limits = {
                'amount': {
                    'min': float(market['minimum_order_amount'][0]),
                    'max': None,
                },
                'price': {
                    'min': math.pow(10, -precision['price']),
                    'max': None,
                },
            }
            limits['cost'] = {
                'min': limits['amount']['min'] * limits['price']['min'],
                'max': None,
            }
            result.append({
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'baseId': baseId,
                'quoteId': quoteId,
                'active': True,
                'precision': precision,
                'limits': limits,
                'info': market,
            })
        return result

    async def fetch_currencies(self, params={}):
        response = await self.publicGetCurrencies()
        currencies = response['currencies']
        result = {}
        for i in range(0, len(currencies)):
            currency = currencies[i]
            if not currency['managed']:
                continue
            id = currency['id']
            code = self.common_currency_code(id)
            precision = currency['input_decimals']
            minimum = math.pow(10, -precision)
            result[code] = {
                'id': id,
                'code': code,
                'info': currency,
                'name': None,
                'active': True,
                'fee': None,
                'precision': precision,
                'limits': {
                    'amount': {
                        'min': minimum,
                        'max': None,
                    },
                    'price': {
                        'min': minimum,
                        'max': None,
                    },
                    'cost': {
                        'min': None,
                        'max': None,
                    },
                    'deposit': {
                        'min': float(currency['deposit_minimum'][0]),
                        'max': None,
                    },
                    'withdraw': {
                        'min': float(currency['withdrawal_minimum'][0]),
                    },
                },
            }
        return result

    async def fetch_funding_fees(self, codes=None, params={}):
        #  by default it will try load withdrawal fees of all currencies(with separate requests)
        #  however if you define codes = ['ETH', 'BTC'] in args it will only load those
        await self.load_markets()
        withdrawFees = {}
        depositFees = {}
        info = {}
        if codes is None:
            codes = list(self.currencies.keys())
        for i in range(0, len(codes)):
            code = codes[i]
            currency = self.currency(code)
            request = {'currency': currency['id']}
            withdrawResponse = await self.publicGetCurrenciesCurrencyFeesWithdrawal(request)
            depositResponse = await self.publicGetCurrenciesCurrencyFeesDeposit(request)
            withdrawFees[code] = self.parse_funding_fee(withdrawResponse['fee'])
            depositFees[code] = self.parse_funding_fee(depositResponse['fee'])
            info[code] = {
                'withdraw': withdrawResponse,
                'deposit': depositResponse,
            }
        return {
            'withdraw': withdrawFees,
            'deposit': depositFees,
            'info': info,
        }

    def parse_funding_fee(self, fee, type=None):
        if type is None:
            type = fee['name']
        if type == 'withdrawal':
            type = 'withdraw'
        return {
            'type': type,
            'currency': fee['base'][1],
            'rate': fee['percent'],
            'cost': float(fee['base'][0]),
        }

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetMarketsMarketTicker(self.extend({
            'market': market['id'],
        }, params))
        ticker = response['ticker']
        return self.parse_ticker(ticker, market)

    def parse_ticker(self, ticker, market=None):
        timestamp = self.milliseconds()
        symbol = None
        if market is not None:
            symbol = market['symbol']
        last = float(ticker['last_price'][0])
        percentage = float(ticker['price_variation_24h'])
        open = float(self.price_to_precision(symbol, last / (percentage + 1)))
        change = last - open
        average = (last + open) / 2
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['max_bid'][0]),
            'bidVolume': None,
            'ask': float(ticker['min_ask'][0]),
            'askVolume': None,
            'vwap': None,
            'open': open,
            'close': last,
            'last': last,
            'previousClose': open,
            'change': change,
            'percentage': percentage * 100,
            'average': average,
            'baseVolume': float(ticker['volume'][0]),
            'quoteVolume': None,
            'info': ticker,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'market': market['id'],
        }
        # the since argument works backwards – returns trades up to the specified timestamp
        # therefore not implemented here
        # the method is still available for users to be able to traverse backwards in time
        # by using the timestamp from the first received trade upon each iteration
        if limit is not None:
            request['limit'] = limit  # 50 max
        response = await self.publicGetMarketsMarketTrades(self.extend(request, params))
        #
        #     {trades: {     market_id:   "ETH-BTC",
        #                      timestamp:    null,
        #                 last_timestamp:   "1536901277302",
        #                        entries: [["1540077456791", "0.0063767", "0.03", "sell", 479842],
        #                                   ["1539916642772", "0.01888263", "0.03019563", "sell", 479438],
        #                                   ["1539834081787", "0.023718648", "0.031001", "sell", 479069],
        #                                   ...]
        #
        return self.parse_trades(response['trades']['entries'], market, since, limit)

    def parse_trade(self, trade, market=None):
        #
        # fetchTrades(public)
        #  ["1540077456791", "0.0063767", "0.03", "sell", 479842]
        #
        timestamp = None
        side = None
        type = None
        price = None
        amount = None
        id = None
        order = None
        fee = None
        symbol = None
        cost = None
        if market:
            symbol = market['symbol']
        if isinstance(trade, list):
            timestamp = int(trade[0])
            price = float(trade[1])
            amount = float(trade[2])
            cost = price * amount
            side = trade[3]
            id = str(trade[4])
        return {
            'id': id,
            'order': order,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': fee,
        }

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        response = await self.publicGetMarketsMarketOrderBook(self.extend({
            'market': market['id'],
        }, params))
        orderBook = response['order_book']
        return self.parse_order_book(orderBook)

    async def fetch_ohlcv(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        if since is None:
            since = self.milliseconds() - 86400000
        request = {
            'symbol': market['id'],
            'resolution': self.timeframes[timeframe],
            'from': since / 1000,
            'to': self.seconds(),
        }
        response = await self.publicGetTvHistory(self.extend(request, params))
        return self.parse_trading_view_ohlcv(response, market, timeframe, since, limit)

    async def fetch_balance(self, params={}):
        await self.load_markets()
        response = await self.privateGetBalances()
        result = {'info': response}
        balances = response['balances']
        for i in range(0, len(balances)):
            balance = balances[i]
            id = balance['id']
            currency = self.common_currency_code(id)
            total = float(balance['amount'][0])
            free = float(balance['available_amount'][0])
            account = {
                'free': free,
                'used': total - free,
                'total': total,
            }
            result[currency] = account
        return self.parse_balance(result)

    async def fetch_order(self, id, symbol=None, params={}):
        await self.load_markets()
        response = await self.privateGetOrdersId(self.extend({
            'id': int(id),
        }, params))
        order = response['order']
        return self.parse_order(order)

    async def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        market = None
        if symbol is not None:
            market = self.market(symbol)
        response = await self.privateGetMarketsMarketOrders(self.extend({
            'market': market['id'],
            'per': limit,
        }, params))
        orders = response['orders']
        return self.parse_orders(orders, market, since, limit)

    async def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        orders = await self.fetch_orders(symbol, since, limit, self.extend({
            'state': 'pending',
        }, params))
        return orders

    async def fetch_closed_orders(self, symbol=None, since=None, limit=None, params={}):
        orders = await self.fetch_orders(symbol, since, limit, self.extend({
            'state': 'traded',
        }, params))
        return orders

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        side = 'Bid' if (side == 'buy') else 'Ask'
        request = {
            'market': self.market_id(symbol),
            'price_type': type,
            'type': side,
            'amount': self.amount_to_precision(symbol, amount),
        }
        if type == 'limit':
            request['limit'] = self.price_to_precision(symbol, price)
        response = await self.privatePostMarketsMarketOrders(self.extend(request, params))
        order = response['order']
        return self.parse_order(order)

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        response = await self.privatePutOrdersId(self.extend({
            'id': int(id),
            'state': 'canceling',
        }, params))
        order = response['order']
        return self.parse_order(order)

    def parse_order_status(self, status):
        statuses = {
            'traded': 'closed',
            'received': 'open',
            'canceling': 'canceled',
        }
        return statuses[status] if (status in list(statuses.keys())) else status

    def parse_order(self, order, market=None):
        id = order['id']
        timestamp = self.parse8601(self.safe_string(order, 'created_at'))
        symbol = None
        if market is None:
            marketId = order['market_id']
            if marketId in self.markets_by_id:
                market = self.markets_by_id[marketId]
        if market is not None:
            symbol = market['symbol']
        type = order['price_type']
        side = order['type'].lower()
        status = self.parse_order_status(self.safe_string(order, 'state'))
        amount = float(order['original_amount'][0])
        remaining = float(order['amount'][0])
        filled = float(order['traded_amount'][0])
        cost = float(order['total_exchanged'][0])
        price = order['limit']
        if price is not None:
            price = float(price[0])
        if cost > 0 and filled > 0:
            price = self.price_to_precision(symbol, cost / filled)
        fee = {
            'cost': float(order['paid_fee'][0]),
            'currency': order['paid_fee'][1],
        }
        return {
            'id': id,
            'datetime': self.iso8601(timestamp),
            'timestamp': timestamp,
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'cost': cost,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'trades': None,
            'fee': fee,
            'info': order,
        }

    def is_fiat(self, code):
        fiats = {
            'ARS': True,
            'CLP': True,
            'COP': True,
            'PEN': True,
        }
        return self.safe_value(fiats, code, False)

    async def fetch_deposit_address(self, code, params={}):
        await self.load_markets()
        currency = self.currency(code)
        if self.is_fiat(code):
            raise NotSupported(self.id + ' fetchDepositAddress() for fiat ' + code + ' is not supported')
        response = await self.privateGetCurrenciesCurrencyReceiveAddresses(self.extend({
            'currency': currency['id'],
        }, params))
        receiveAddresses = response['receive_addresses']
        addressPool = []
        for i in range(1, len(receiveAddresses)):
            receiveAddress = receiveAddresses[i]
            if receiveAddress['ready']:
                address = receiveAddress['address']
                self.check_address(address)
                addressPool.append(address)
        addressPoolLength = len(addressPool)
        if addressPoolLength < 1:
            raise AddressPending(self.name + ': there are no addresses ready for receiving ' + code + ', retry again later)')
        address = addressPool[0]
        return {
            'currency': code,
            'address': address,
            'tag': None,
            'info': receiveAddresses,
        }

    async def create_deposit_address(self, code, params={}):
        await self.load_markets()
        currency = self.currency(code)
        if self.is_fiat(code):
            raise NotSupported(self.name + ': fiat fetchDepositAddress() for ' + code + ' is not supported')
        response = await self.privatePostCurrenciesCurrencyReceiveAddresses(self.extend({
            'currency': currency['id'],
        }, params))
        address = self.safe_string(response['receive_address'], 'address')  # the creation is async and returns a null address, returns only the id
        return {
            'currency': code,
            'address': address,
            'tag': None,
            'info': response,
        }

    def parse_transaction_status(self, status):
        statuses = {
            'rejected': 'failed',
            'confirmed': 'ok',
            'anulled': 'canceled',
            'retained': 'canceled',
            'pending_confirmation': 'pending',
        }
        return statuses[status] if (status in list(statuses.keys())) else status

    def parse_transaction(self, transaction, currency=None):
        id = self.safe_string(transaction, 'id')
        timestamp = self.parse8601(self.safe_string(transaction, 'created_at'))
        code = None
        currencyId = None
        if currency is None:
            currencyId = self.safe_string(transaction, 'currency')
            currency = self.safe_value(self.currencies_by_id, currencyId)
        if currency is not None:
            code = currency['code']
        else:
            code = self.common_currency_code(currencyId)
        amount = float(transaction['amount'][0])
        fee = float(transaction['fee'][0])
        feeCurrency = transaction['fee'][1]
        status = self.parse_transaction_status(self.safe_string(transaction, 'state'))
        type = 'deposit' if ('deposit_data' in list(transaction.keys())) else 'withdrawal'
        data = self.safe_value(transaction, type + '_data', {})
        address = self.safe_value(data, 'target_address')
        txid = self.safe_string(data, 'tx_hash')
        updated = self.parse8601(self.safe_string(data, 'updated_at'))
        return {
            'info': transaction,
            'id': id,
            'txid': txid,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'address': address,
            'type': type,
            'amount': amount,
            'currency': code,
            'status': status,
            'updated': updated,
            'fee': {
                'cost': fee,
                'rate': feeCurrency,
            },
        }

    async def fetch_deposits(self, code=None, since=None, limit=None, params={}):
        await self.load_markets()
        if code is None:
            raise ExchangeError(self.name + ': fetchDeposits() requires a currency code argument')
        currency = self.currency(code)
        response = await self.privateGetCurrenciesCurrencyDeposits(self.extend({
            'currency': currency['id'],
            'per': limit,
        }, params))
        deposits = response['deposits']
        return self.parseTransactions(deposits, currency, since, limit)

    async def fetch_withdrawals(self, code=None, since=None, limit=None, params={}):
        await self.load_markets()
        if code is None:
            raise ExchangeError(self.name + ': fetchDeposits() requires a currency code argument')
        currency = self.currency(code)
        response = await self.privateGetCurrenciesCurrencyWithdrawals(self.extend({
            'currency': currency['id'],
            'per': limit,
        }, params))
        withdrawals = response['withdrawals']
        return self.parseTransactions(withdrawals, currency, since, limit)

    async def withdraw(self, code, amount, address, tag=None, params={}):
        self.check_address(address)
        await self.load_markets()
        currency = self.currency(code)
        response = await self.privatePostCurrenciesCurrencyWithdrawals(self.extend({
            'currency': currency['id'],
            'amount': amount,
            'withdrawal_data': {
                'target_address': address,
            },
        }, params))
        withdrawal = response['withdrawal']
        return self.parse_transaction(withdrawal)

    def nonce(self):
        return self.microseconds()

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        request = self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if query:
            if method == 'GET':
                request += '?' + self.urlencode(query)
            else:
                body = self.json(query)
        url = self.urls['api'] + '/' + self.version + '/' + request
        if api == 'private':
            self.check_required_credentials()
            nonce = str(self.nonce())
            components = [method, '/api/' + self.version + '/' + request]
            if body:
                base64_body = base64.b64encode(self.encode(body))
                components.append(self.decode(base64_body))
            components.append(nonce)
            message = ' '.join(components)
            signature = self.hmac(self.encode(message), self.encode(self.secret), hashlib.sha384)
            headers = {
                'X-SBTC-APIKEY': self.apiKey,
                'X-SBTC-SIGNATURE': signature,
                'X-SBTC-NONCE': nonce,
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, code, reason, url, method, headers, body):
        if not self.is_json_encoded_object(body):
            return  # fallback to default error handler
        if code >= 400:
            response = json.loads(body)
            errorCode = self.safe_string(response, 'code')
            message = self.safe_string(response, 'message', body)
            feedback = self.name + ': ' + message
            exceptions = self.exceptions
            if errorCode is not None:
                if errorCode in exceptions:
                    raise exceptions[errorCode](feedback)
                else:
                    raise ExchangeError(feedback)
