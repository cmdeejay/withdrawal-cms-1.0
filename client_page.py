from typing import Any
from api_methods import API_METHODS
from processing import BaseProcessing
from selenium.common.exceptions import JavascriptException
import time
import sqlite3
import datetime
import pandas as pd


class ClientPages(BaseProcessing):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def _preparation(self, **kwargs) -> None:
        self._get(url="https://global-cms.fxtm/")

    def _load_to_database(self, balance_map, **kwargs):
        data = pd.DataFrame([balance_map])
        with sqlite3.connect(f"{kwargs.get('sqlite')}") as conn:
            data.to_sql(
                f"{kwargs.get('table')}",
                conn,
                if_exists="append",
                index=False,
            )
            conn.commit()
