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
from qf_lib.containers.dataframe.prices_dataframe import PricesDataFrame


class FutureContract(object):
    def __init__(self, ticker: Ticker, exp_date: datetime, data: PricesDataFrame):
        """
        Parameters
        ----------
        ticker
            symbol of the future contract
        exp_date
            expiration date
        data
            data frame containing dates with price fields values
        """
        self.ticker = ticker
        self.exp_date = exp_date
        self.data = data

    def __str__(self):
        return 'Contract: ticker: {}, expiration date: {}'.format(
            self.ticker, self.exp_date)

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, FutureContract):
            return False

        return (self.ticker, self.exp_date, self.data) == (other.ticker, other.exp_date, other.data)

    def __hash__(self):
        return hash((self.ticker, self.exp_date, self.data))
