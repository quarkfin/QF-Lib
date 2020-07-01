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

from qf_lib.common.utils.returns.drawdown_tms import drawdown_tms
from qf_lib.containers.series.qf_series import QFSeries


def avg_drawdown(prices_tms: QFSeries) -> float:
    """
    Finds the average drawdown for the given timeseries of prices.

    Parameters
    ----------
    prices_tms: QFSeries
        timeseries of prices

    Returns
    -------
    float
        average drawdown for the given timeseries of prices expressed as the percentage value (e.g. 0.5 corresponds
        to the 50% drawdown)
    """

    return drawdown_tms(prices_tms).mean()
