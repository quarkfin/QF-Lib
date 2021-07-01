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

from abc import abstractmethod, ABCMeta

from qf_lib.backtesting.alpha_model.exposure_enum import Exposure
from qf_lib.backtesting.signals.signal import Signal
from qf_lib.backtesting.data_handler.data_handler import DataHandler
from qf_lib.common.enums.price_field import PriceField
from qf_lib.common.tickers.tickers import Ticker
from qf_lib.common.utils.miscellaneous.average_true_range import average_true_range


class AlphaModel(object, metaclass=ABCMeta):
    """
    Base class for all alpha models.

    Parameters
    ----------
    risk_estimation_factor
        float value which estimates the risk level of the specific AlphaModel. Corresponds to the level at which
        the stop-loss should be placed.
    data_handler
        DataHandler which provides data for the ticker
    """

    def __init__(self, risk_estimation_factor: float, data_handler: DataHandler):
        self.risk_estimation_factor = risk_estimation_factor
        self.data_handler = data_handler

    def get_signal(self, ticker: Ticker, current_exposure: Exposure) -> Signal:
        """
        Returns the Signal calculated for a specific AlphaModel and a set of data for a specified Ticker

        Parameters
        ----------
        ticker: Ticker
            A ticker of an asset for which the Signal should be generated
        current_exposure: Exposure
            The actual exposure, based on which the AlphaModel should return its Signal. Can be different from previous
            Signal suggestions, but it should correspond with the current trading position

        Returns
        -------
        Signal
            Signal being the suggestion for the next trading period
        """
        suggested_exposure = self.calculate_exposure(ticker, current_exposure)
        fraction_at_risk = self.calculate_fraction_at_risk(ticker)
        last_available_price = self.data_handler.get_last_available_price(ticker)

        signal = Signal(ticker, suggested_exposure, fraction_at_risk, last_available_price, alpha_model=self)
        return signal

    @abstractmethod
    def calculate_exposure(self, ticker: Ticker, current_exposure: Exposure) -> Exposure:
        """
        Returns the expected Exposure, which is the key part of a generated Signal. Exposure suggests the trend
        direction for managing the trading position.
        Uses DataHandler passed when the AlphaModel (child) is initialized - all required data is provided in the child
        class.

        Parameters
        ----------
        ticker: Ticker
            Ticker for which suggested signal exposure is calculated.
        current_exposure: Exposure
            The actual exposure, based on which the AlphaModel should return its Signal. Can be different from previous
            Signal suggestions, but it should correspond with the current trading position

        """
        pass

    def calculate_fraction_at_risk(self, ticker: Ticker) -> float:
        """
        Returns the float value which determines the risk factor for an AlphaModel and a specified Ticker,
        may be used to calculate the position size.

        For example: Value of 0.02 means that we should place a Stop Loss 2% below the latest available
        price of the instrument. This value should always be positive

        Parameters
        ----------
        ticker: Ticker
            Ticker for which the calculation should be made

        Returns
        -------
        float
            percentage_at_risk value for an AlphaModel and a Ticker, calculated as Normalized Average True Range
            multiplied by the risk_estimation_factor, being a property of each AlphaModel:
            fraction_at_risk = ATR / last_close * risk_estimation_factor

        """
        time_period = 5
        return self._atr_fraction_at_risk(ticker, time_period)

    def _atr_fraction_at_risk(self, ticker, time_period):
        """
        Parameters
        ----------
        ticker
            Ticker for which the calculation should be made
        time_period
            time period in days for which the ATR is calculated

        Returns
        -------
            fraction_at_risk value for an AlphaModel and a Ticker, calculated as Normalized Average True Range
            multiplied by the risk_estimation_factor, being a property of each AlphaModel:
            fraction_at_risk = ATR / last_close * risk_estimation_factor
        """
        num_of_bars_needed = time_period + 1
        fields = [PriceField.High, PriceField.Low, PriceField.Close]
        prices_df = self.data_handler.historical_price(ticker, fields, num_of_bars_needed)
        fraction_at_risk = average_true_range(prices_df, normalized=True) * self.risk_estimation_factor
        return fraction_at_risk

    def __str__(self):
        return self.__class__.__name__

    def __hash__(self):
        return hash((self.__class__.__name__, self.risk_estimation_factor,))
