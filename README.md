FAVS
====

A python package for Fundamentals-based Automated Valuation of Stocks. 

Installation
------------
The [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) executable needs to be somewhere in your PATH. 

Usage
-----

Discounted Free Cash Flow (DFCF) valuation:

``` python
from favs.models.fcf import dfcf

symbol = 'AAPL'

print(dfcf(symbol))

```

