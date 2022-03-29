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
from unittest import TestCase

import matplotlib

from qf_lib.backtesting.broker.broker import Broker
from qf_lib.backtesting.events.time_event.regular_time_event.before_market_open_event import BeforeMarketOpenEvent
from qf_lib.backtesting.order.time_in_force import TimeInForce
from qf_lib.common.enums.frequency import Frequency
from qf_lib_tests.helpers.testing_tools.containers_comparison import assert_series_equal
from qf_lib_tests.integration_tests.connect_to_data_provider import get_data_provider

from qf_lib_tests.integration_tests.backtesting.trading_session_for_tests import TradingSessionForTests
from qf_lib.backtesting.order.execution_style import MarketOrder
from qf_lib.common.enums.price_field import PriceField

from qf_lib.backtesting.events.time_event.scheduler import Scheduler
from qf_lib.backtesting.order.order_factory import OrderFactory
from qf_lib.common.tickers.tickers import BloombergTicker
from qf_lib.common.utils.dateutils.string_to_date import str_to_date
from qf_lib.data_providers.general_price_provider import GeneralPriceProvider

matplotlib.use("Agg")


class BuyAndHoldStrategy:
    """
    A testing strategy that simply purchases (longs) an asset as soon as it starts and then holds until the completion
    of a backtest.
    """
    MICROSOFT_TICKER = BloombergTicker("MSFT US Equity")

    def __init__(self, broker: Broker, order_factory: OrderFactory, scheduler: Scheduler):
        self.order_factory = order_factory
        self.broker = broker

        self.invested = False

        scheduler.subscribe(BeforeMarketOpenEvent, listener=self)

    def on_before_market_open(self, _: BeforeMarketOpenEvent):
        self.calculate_signals()

    def calculate_signals(self):
        if not self.invested:
            orders = self.order_factory.percent_orders({self.MICROSOFT_TICKER: 1.0}, MarketOrder(),
                                                       TimeInForce.GTC)
            self.broker.place_orders(orders)
            self.invested = True


class TestBacktester(TestCase):
    def setUp(self):
        try:
            self.data_provider = get_data_provider()
        except Exception as e:
            raise self.skipTest(e)

    def test_backtester_with_buy_and_hold_strategy(self):
        start_date = str_to_date("2010-01-01")
        end_date = str_to_date("2010-02-01")
        data_provider = GeneralPriceProvider(self.data_provider, None, None)

        msft_prices = data_provider.get_price(
            BuyAndHoldStrategy.MICROSOFT_TICKER, fields=[PriceField.Open, PriceField.Close],
            start_date=str_to_date("2009-12-28"), end_date=str_to_date("2010-02-01")
        )

        first_trade_date = str_to_date("2010-01-04")
        initial_cash = msft_prices.loc[first_trade_date, PriceField.Open]
        ts = TradingSessionForTests(data_provider, start_date, end_date, initial_cash, frequency=Frequency.DAILY)

        BuyAndHoldStrategy(ts.broker, ts.order_factory, ts.notifiers.scheduler)

        # Set up the backtest
        ts.start_trading()

        actual_portfolio_tms = ts.portfolio.portfolio_eod_series()

        expected_portfolio_tms = msft_prices.loc[:, PriceField.Close].asof(actual_portfolio_tms.index)
        expected_portfolio_tms[:str_to_date("2010-01-03")] = initial_cash

        assert_series_equal(expected_portfolio_tms, actual_portfolio_tms, check_names=False)


if __name__ == "__main__":
    unittest.main()
