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

from abc import ABCMeta, abstractmethod
from typing import Union

from qf_lib.backtesting.contract.contract import Contract
from qf_lib.common.tickers.tickers import Ticker
from qf_lib.containers.futures.future_tickers.future_ticker import FutureTicker


class ContractTickerMapper(metaclass=ABCMeta):
    @abstractmethod
    def contract_to_ticker(self, contract: Contract, strictly_to_specific_ticker=True) -> Union[Ticker, FutureTicker]:
        """Maps Contract object onto corresponding Ticker.

        Parameters
        ----------
        contract: Contract
            contract that should be mapped
        strictly_to_specific_ticker: bool
            allows to map a Future contract to either Ticker (default) or FutureTicker

        Returns
        -------
        Ticker
            corresponding ticker
        """
        pass

    @abstractmethod
    def ticker_to_contract(self, ticker: Ticker) -> Contract:
        """Maps ticker to corresponding ticker.

        Parameters
        ----------
        ticker: Ticker
            ticker that should be mapped

        Returns
        -------
        Contract
            corresponding contract
        """
        pass

    def __str__(self):
        return self.__class__.__name__
