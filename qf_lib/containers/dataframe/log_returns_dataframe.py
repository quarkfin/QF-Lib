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

from qf_lib.containers.dataframe.qf_dataframe import QFDataFrame


class LogReturnsDataFrame(QFDataFrame):
    """
    DataFrame containing log-returns.
    """
    @property
    def _constructor_sliced(self):
        from qf_lib.containers.series.log_returns_series import LogReturnsSeries
        return LogReturnsSeries

    @property
    def _constructor(self):
        return LogReturnsDataFrame
