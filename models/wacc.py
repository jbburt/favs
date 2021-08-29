from typing import Type

from scrape.base import BaseDataLoader

__all__ = ['wacc']


def wacc(client: Type[BaseDataLoader],
         rfr: float = 1.26,
         market_ret: float = 10.0,

         ) -> float:
    """
    Weighted-average cost of capital.

    Parameters
    ----------
    client : Type[BaseDataLoader]
    rfr : float, optional (default 1.26)
        risk-free rate, expressed as a percent
    market_ret : float, optional (default 10.0)
        forecasted market return, expressed as a percent

    Returns
    -------
    float : wacc expressed as a percent

    """
    beta = client.beta
    raise NotImplementedError
