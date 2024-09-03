#     Copyright 2016-present CERN – European Organization for Nuclear Research
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

import unittest
from unittest.mock import Mock
from qf_lib.backtesting.data_handler.data_handler import DataHandler
from qf_lib.backtesting.portfolio.portfolio import Portfolio
from qf_lib.backtesting.portfolio.transaction import Transaction
from qf_lib.common.enums.security_type import SecurityType
from qf_lib.common.tickers.exchange_rate_ticker import CurrencyExchangeTicker
from qf_lib.common.utils.dateutils.timer import SettableTimer
from qf_lib.containers.series.prices_series import PricesSeries
from qf_lib.containers.series.qf_series import QFSeries
from qf_lib.tests.helpers.testing_tools.containers_comparison import assert_series_equal
from qf_lib.tests.unit_tests.backtesting.portfolio.dummy_ticker import DummyExchangeTicker, DummyTicker
from qf_lib.tests.unit_tests.backtesting.portfolio.test_portfolio import TestPortfolio


class TestPortfolioWithCurrency(TestPortfolio):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.currency = "CHF"
        cls.currency_exchange_tickers = [
            DummyExchangeTicker("USDCHF Curncy", from_currency="USD", to_currency="CHF")]

        cls.ticker = DummyTicker('AAPL US Equity', SecurityType.STOCK, currency="USD")
        cls.fut_ticker = DummyTicker('CTZ9 Comdty', SecurityType.FUTURE, cls.point_value, "USD")

        tickers = [cls.ticker, cls.fut_ticker, cls.currency_exchange_tickers[0]]
        cls.prices_series = QFSeries(data=[120, 250, 0.95], index=tickers)
        cls.prices_up = QFSeries(data=[130, 270, 0.98], index=tickers)
        cls.prices_down = QFSeries(data=[100, 210, 0.98], index=tickers)

    def setUp(self) -> None:
        self.data_handler_prices = None

    def get_portfolio_and_data_handler(self):
        data_handler = Mock(spec=DataHandler)
        data_handler.get_last_available_price.side_effect = lambda tickers: self.data_handler_prices[tickers] \
            if tickers else None

        timer = SettableTimer()
        timer.set_current_time(self.start_time)

        portfolio = Portfolio(data_handler, self.initial_cash, timer, currency=self.currency,
                              currency_exchange_tickers=self.currency_exchange_tickers)
        return portfolio, data_handler, timer

    def test_transact_transaction_1(self):
        portfolio, data_handler, _ = self.get_portfolio_and_data_handler()

        self.data_handler_prices = self.prices_series

        transaction = Transaction(self.random_time, self.ticker, quantity=50, price=100, commission=5, )
        portfolio.transact_transaction(transaction)

        cash_move_1 = self._cash_move(transaction)
        cash_move_1 *= data_handler.get_last_available_price(self.currency_exchange_tickers[0])

        self.assertEqual(portfolio.initial_cash, self.initial_cash)
        self.assertEqual(portfolio.net_liquidation, self.initial_cash)
        self.assertEqual(portfolio.gross_exposure_of_positions, 0)  # not yet updated
        self.assertEqual(portfolio.current_cash, self.initial_cash + cash_move_1)
        self.assertEqual(len(portfolio.open_positions_dict), 1)

    def test_portfolio_eod_series(self):
        expected_portfolio_eod_series = PricesSeries()

        # Empty portfolio
        portfolio, dh, timer = self.get_portfolio_and_data_handler()
        portfolio.update(record=True)
        expected_portfolio_eod_series[timer.time] = self.initial_cash

        self.data_handler_prices = self.prices_series

        # Buy contract
        self._shift_timer_to_next_day(timer)
        transaction_1 = Transaction(timer.time, self.fut_ticker, quantity=50, price=250, commission=7)
        portfolio.transact_transaction(transaction_1)
        portfolio.update(record=True)

        price_1 = dh.get_last_available_price(self.fut_ticker)
        pnl = self.fut_ticker.point_value * transaction_1.quantity * (price_1 - transaction_1.price) - transaction_1.commission
        pnl *= dh.get_last_available_price(self.currency_exchange_tickers[0])
        nav = self.initial_cash + pnl
        expected_portfolio_eod_series[timer.time] = nav

        # Contract goes up in value
        self._shift_timer_to_next_day(timer)
        self.data_handler_prices = self.prices_up
        portfolio.update(record=True)

        price_2 = dh.get_last_available_price(self.fut_ticker)  # == 270
        pnl = self.fut_ticker.point_value * transaction_1.quantity * (price_2 - price_1)
        pnl *= dh.get_last_available_price(self.currency_exchange_tickers[0])
        nav += pnl
        expected_portfolio_eod_series[timer.time] = nav

        # Sell part of the contract
        self._shift_timer_to_next_day(timer)
        self.data_handler_prices = self.prices_up
        transaction_2 = Transaction(timer.time, self.fut_ticker, quantity=-25, price=price_2, commission=19)
        portfolio.transact_transaction(transaction_2)
        portfolio.update(record=True)

        pnl = (transaction_2.price - price_2) * transaction_2.quantity * self.fut_ticker.point_value - \
            transaction_2.commission
        pnl *= dh.get_last_available_price(self.currency_exchange_tickers[0])
        nav += pnl
        expected_portfolio_eod_series[timer.time] = nav

        # Price goes down
        self._shift_timer_to_next_day(timer)
        self.data_handler_prices = self.prices_down
        portfolio.update(record=True)

        position = portfolio.open_positions_dict[self.fut_ticker]

        price_3 = dh.get_last_available_price(self.fut_ticker)  # == 210
        pnl2 = self.fut_ticker.point_value * position.quantity() * (price_3 - price_2)
        pnl2 *= dh.get_last_available_price(self.currency_exchange_tickers[0])
        nav += pnl2
        expected_portfolio_eod_series[timer.time] = nav

        tms = portfolio.portfolio_eod_series()
        assert_series_equal(expected_portfolio_eod_series, tms)


if __name__ == "__main__":
    unittest.main()
