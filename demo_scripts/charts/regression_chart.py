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

import matplotlib.pyplot as plt

from demo_scripts.common.utils.dummy_ticker import DummyTicker
from demo_scripts.demo_configuration.demo_data_provider import daily_data_provider
from qf_lib.common.enums.price_field import PriceField
from qf_lib.common.utils.dateutils.string_to_date import str_to_date
from qf_lib.plotting.charts.regression_chart import RegressionChart

start_date = str_to_date('2006-01-01')
end_date = str_to_date('2018-12-31')


def main():
    data_provider = daily_data_provider
    benchmark_tms = data_provider.get_price(DummyTicker('AAA'), PriceField.Close, start_date, end_date)
    strategy_tms = data_provider.get_price(DummyTicker('BBB'), PriceField.Close, start_date, end_date)

    regression_chart = RegressionChart(benchmark_tms=benchmark_tms, strategy_tms=strategy_tms)
    regression_chart.plot()

    plt.show(block=True)


if __name__ == '__main__':
    main()
