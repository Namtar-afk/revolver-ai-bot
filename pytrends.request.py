# bot/monitoring.py  (ou utils/patches.py si tu préfères isoler)
import warnings
from contextlib import contextmanager

import pandas as pd


@contextmanager
def silence_pytrends_futurewarning():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=FutureWarning,
            message="Downcasting object dtype.*fillna",
            module="pytrends.request",
        )
        yield


# usage dans la fonction qui appelle pytrends
with silence_pytrends_futurewarning():
    df = pytrends.interest_over_time()
