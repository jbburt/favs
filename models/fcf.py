""" Discounted free cash flow """

from typing import Type
from typing import Union

import numpy as np
import pandas as pd

from scrape import yahoo
from scrape.base import BaseDataLoader

__all__ = ['dfcf']


def dfcf(symbol: str,
         client_class: Type[BaseDataLoader] = yahoo.Client,
         required_ret: Union[str, float] = 7.5,
         perp_growth: float = 2.5,
         ) -> float:
    """
    Discounted future cash flow valuation.

    Parameters
    ----------
    symbol: str
        stock ticker symbol
    client_class : Type[BaseDataLoader], optional (default scrape.yahoo.Client)
        client object with access to data
    required_ret : str or float, optional (default 7.5)
        if float, the required return expressed as a percent. passing 'wacc'
        computes the weighted averaged cost of capital and uses that value as
        the required return
    perp_growth : float, optional (default 2.5)
        perpetual growth rate of market expressed as percent, typically somewhere
        between the historical inflation rate of 2-3% and the historical GDP
        growth rate of 4-5%

    Returns
    -------
    float : DFCF valuation amount

    """

    client = client_class()
    client.load_data(symbol)

    # TODO add option to pull RFR from ^TNX price
    if not client.is_loaded:
        raise RuntimeError('no stock information has been loaded')

    if required_ret == 'wacc':
        raise NotImplementedError

    cf = client.cash_flow
    ist = client.income_statement
    # bs = client.balance_sheet

    # free cash flow to equity
    fcf = cf.loc['Operating Cash Flow'] - cf.loc['Capital Expenditure']

    # net income and ratio of free cash flow to income
    net_income = ist.loc['Net Income Common Stockholders']
    ratio = fcf / net_income
    net_income.drop('ttm', axis=0, inplace=True)
    net_income.index = net_income.index.astype(int)

    # Forecasted FCF to Net Income ratio
    forecast_ratio = ratio.drop('ttm').mean()  # TODO make parameter

    # Historical revenues
    rev = ist.loc['Total Revenue']
    rev.drop('ttm', axis=0, inplace=True)
    rev.index = rev.index.astype(int)
    rev = rev.loc[rev.values > 0]

    # Projected revenues
    try:
        rev_proj = client.projections.Revenue
    except AttributeError:
        raise RuntimeError('Analyst projections for revenue were not found')

    # Revenue growth
    rev_all = pd.concat(
        (rev, client.projections.Revenue)
    ).sort_index()
    rev_growth = rev_all.diff().div(
        rev_all.shift(1)).replace(
        [np.inf, -np.inf], np.nan).dropna()

    # Forecasted revenue growth
    forecast_rev_growth = rev_growth.dropna().mean()  # todo make param

    # Projected revenue, two years out from last analyst estimate
    last_year = rev_proj.index.max()
    proj_next = rev_proj.loc[last_year] * (1 + forecast_rev_growth)
    proj_next2 = proj_next * (1 + forecast_rev_growth)
    rev_proj[last_year + 1] = proj_next
    rev_proj[last_year + 2] = proj_next2

    # Net Income margins
    income_margins = net_income.div(rev).sort_index()

    # Forecasted net income margin
    forecast_margin = income_margins.mean()  # todo make param

    # Projected net income
    proj_net_income = rev_proj * forecast_margin

    # Projected FCF
    proj_fcf = proj_net_income * forecast_ratio
    proj_fcf_term = proj_fcf.loc[proj_fcf.index.max()] * (1 + required_ret / 100) / (
            (required_ret - perp_growth) / 100
    )

    # Discount factors
    factors = (1 + required_ret / 100) ** np.arange(1, rev_proj.shape[0] + 1)

    # Present value of future cash flows
    pv_fcf = proj_fcf / factors
    pv_fcf_term = proj_fcf_term / factors.max()

    # today's value
    value_today = pv_fcf.sum() + pv_fcf_term

    return round(value_today / client.shares * 1000, 2)
