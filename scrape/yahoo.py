import re
from typing import List

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scrape.base import BaseDataLoader


class Client(BaseDataLoader):

    def __init__(self):
        super().__init__()
        options = Options()
        options.add_argument('--headless')
        self._driver = webdriver.Chrome(options=options)

    def load_data(self, symbol: str) -> None:
        super().load_data(symbol)
        self._driver.close()
        self._driver.quit()

    def load_stats(self, symbol: str) -> None:
        url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
        self._stats = self._load_statistics(url)

    def load_projections(self, symbol: str) -> None:
        url = f"https://finance.yahoo.com/quote/{symbol}/analysis?p={symbol}"
        tables = self._load_analysis(url)

        # parse revenue estimates
        df = tables[1]  # revenue table
        # [re.search(r'\((.*?)\)',s).group(1) for s in df.loc['Avg. Estimate'].index]
        assert 'Current Year' in df.columns.values[-2]
        assert 'Next Year' in df.columns.values[-1]
        index = [int(re.search(r'\((.*?)\)', s).group(1)) for s in
                 df.loc['Avg. Estimate'].iloc[-2:].index]
        values = [pd.to_numeric(s.replace('B', 'e6').replace('M', 'e3')) for s in
                  df.loc['Avg. Estimate'].iloc[-2:].values]
        self._projections = pd.DataFrame(
            index=index, columns=['Revenue'], data=values)

    def load_income_statement(self, symbol: str) -> None:
        url = f"https://finance.yahoo.com/quote/{symbol}/financials?p={symbol}"
        self._income_statement = self._load_page(url)

    def load_balance_sheet(self, symbol: str) -> None:
        url = f"https://finance.yahoo.com/quote/{symbol}/balance-sheet?p={symbol}"
        self._balance_sheet = self._load_page(url)

    def load_cash_flow(self, symbol: str) -> None:
        url = f"https://finance.yahoo.com/quote/{symbol}/cash-flow?p={symbol}"
        self._cash_flow = self._load_page(url)

    def _load_page(self, url: str) -> pd.DataFrame:
        self._driver.get(url)
        html = self._driver.execute_script('return document.body.innerHTML;')
        soup = BeautifulSoup(html, 'lxml')
        features = soup.find_all('div', class_='D(tbr)')

        # create headers
        headers = []
        for item in features[0].find_all('div', class_='D(ib)'):
            headers.append(item.text)

        # statement contents
        statement = [
            [l.text for l in f.find_all('div', class_='D(tbc)')] for f in features
        ]

        df = pd.DataFrame(statement[1:])
        df.columns = [x[-4:] for x in headers]
        df.set_index('down', inplace=True)
        df.index.name = ''
        return df.applymap(  # convert strings to numeric
            lambda s: pd.to_numeric(s.replace(',', '').replace('-', '')))

    def _load_analysis(self, url: str) -> List[pd.DataFrame]:
        self._driver.get(url)
        html = self._driver.execute_script('return document.body.innerHTML;')
        soup = BeautifulSoup(html, 'lxml')
        tables = soup.find_all('table')

        dfs = list()
        for table in tables:
            columns = [th.text for th in table.find('thead').find_all('th')]
            name = columns.pop(0)
            index = [
                td.text for td in table.find_all('td', class_="Ta(start)")
            ]
            values = np.array(
                [td.text for td in table.find_all('td', class_='Ta(end)')]
            ).reshape((len(index), len(columns)), order='C')
            df = pd.DataFrame(
                index=index, columns=columns, data=values)
            df.index.name = name
            dfs.append(df)
        return dfs

    def _load_statistics(self, url: str) -> pd.Series:
        self._driver.get(url)
        html = self._driver.execute_script('return document.body.innerHTML;')
        soup = BeautifulSoup(html, 'lxml')
        tables = soup.find_all('table')

        # TODO parse all info from statistics page

        # beta
        col, beta = [e.text for e in tables[1].find_all('tr')[0].find_all('td')]
        assert 'Beta' in col
        try:
            series = pd.Series(index=['Beta'], data=float(beta))
        except ValueError:
            series = pd.Series(index=['Beta'], data=np.nan)

        # shares outstanding
        col, shares = [e.text for e in tables[2].find_all('tr')[2].find_all('td')]
        assert 'Shares Outstanding' in col
        series['SharesOutstanding'] = pd.to_numeric(
            shares.replace('B', 'e9').replace('M', 'e6'))
        return series
