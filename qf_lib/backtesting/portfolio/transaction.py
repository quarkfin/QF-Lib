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

from datetime import datetime

from qf_lib.common.tickers.tickers import Ticker
from qf_lib.common.utils.dateutils.date_to_string import date_to_str


class Transaction:
    """
    Encapsulates the notion of a filled Order, as returned from a Brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores the commission of the trade from the Brokerage.

    Parameters
    ----------
    time: datetime
        time when the order was filled
    ticker: Ticker
        ticker identifying the asset
    quantity: int
        filled quantity, positive for assets bought and negative for assets sold
    price: float
        price at which the trade was filled
    commission: float
        brokerage commission for carrying out the trade. It is always a positive number
    """

    def __init__(self, time: datetime, ticker: Ticker, quantity: int, price: float, commission: float):
        assert commission >= 0.0

        self.time = time
        self.ticker = ticker
        self.quantity = quantity
        self.price = price
        self.commission = commission

    def __str__(self):
        return f"{self.__class__.__name__} ({date_to_str(self.time)}) -> " \
               f"Quantity: {self.quantity:>8}, " \
               f"Price: {self.price:>10.2f}, " \
               f"Commission: {self.commission:>7.2f}, " \
               f"Ticker: {str(self.ticker):}"

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, Transaction):
            return False

        return (self.time, self.ticker, self.quantity, self.price, self.commission) == \
               (other.time, other.ticker, other.quantity, other.price, other.commission)
