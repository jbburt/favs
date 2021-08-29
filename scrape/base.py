import copy
from abc import ABC
from abc import abstractmethod
from typing import Union

import pandas as pd


class BaseDataLoader(ABC):

    def __init__(self):

        self._symbol: Union[None, str] = None
        self._income_statement: Union[None, pd.DataFrame] = None
        self._cash_flow: Union[None, pd.DataFrame] = None
        self._balance_sheet: Union[None, pd.DataFrame] = None
        self._projections: Union[None, pd.DataFrame] = None
        self._stats: Union[None, pd.Series] = None
        self._is_loaded: bool = False

    def load_data(self, symbol: str) -> None:
        self._symbol = symbol
        self.load_income_statement(symbol)
        self.load_balance_sheet(symbol)
        self.load_cash_flow(symbol)
        self.load_projections(symbol)
        self.load_stats(symbol)
        self._is_loaded = True

    @abstractmethod
    def load_projections(self, symbol: str) -> None:
        pass

    @abstractmethod
    def load_income_statement(self, symbol: str) -> None:
        pass

    @abstractmethod
    def load_balance_sheet(self, symbol: str) -> None:
        pass

    @abstractmethod
    def load_cash_flow(self, symbol: str) -> None:
        pass

    @abstractmethod
    def load_stats(self, symbol: str) -> None:
        pass

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def income_statement(self) -> Union[None, pd.DataFrame]:
        if self._income_statement is None:
            return None
        return self._income_statement.copy()

    @property
    def balance_sheet(self) -> Union[None, pd.DataFrame]:
        if self._balance_sheet is None:
            return None
        return self._balance_sheet.copy()

    @property
    def cash_flow(self) -> Union[None, pd.DataFrame]:
        if self._cash_flow is None:
            return None
        return self._cash_flow.copy()

    @property
    def projections(self) -> Union[None, pd.DataFrame]:
        if self._projections is None:
            return None
        return self._projections.copy()

    @property
    def stats(self) -> Union[pd.Series, None]:
        if self._stats is None:
            return None
        return self._stats.copy()

    @property
    def beta(self) -> Union[float, None]:
        if self._stats is None:
            return None
        return self._stats.Beta

    @property
    def shares(self) -> Union[int, None]:
        if self._stats is None:
            return None
        return int(self._stats.SharesOutstanding)

    @property
    def is_loaded(self) -> bool:
        return copy.deepcopy(self._is_loaded)
