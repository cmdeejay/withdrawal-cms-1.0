from typing import Any
from api_methods import API_METHODS
from processing import BaseProcessing
from selenium.common.exceptions import JavascriptException
import time
import sqlite3
import datetime
import pandas as pd
from client_page import ClientPages


def read_client_id():
    with sqlite3.connect("../trading_account/trading_account.sqlite") as conn:
        df = pd.read_sql_query(
            """SELECT 
                                "MY" AS "Client ID",
                                --"Group",
                                COUNT("Login") total
                                FROM tranding_account ta 
                                GROUP BY 
                                "Client ID"
                                --"Group"
                                HAVING "total" > 10
                                ORDER BY "total" DESC""",
            conn,
        )
    return df


def main():
    df = read_client_id()
    client_ids = df["Client ID"].tolist()
    print(len(client_ids))
    get_client_balance = ClientPages()
    get_client_balance._preparation()
    balance_map = {}
    for client_id in client_ids:
        get_client_balance._go_to_clients(client_id=client_id)
        client_balance = get_client_balance._total_balance()
        print(client_balance)
        time.sleep(1)
        get_client_balance._payments_tab()
        time.sleep(1)
        if get_client_balance._open_first_transaction():
            time.sleep(1)
            transfer_volume = get_client_balance._summary_total()
            deposit_amount = transfer_volume.get("Deposit USD")
            withdrawal_amount = transfer_volume.get("Withdrawal USD")
            time.sleep(1)
            balance_map = {
                "client_id": client_id,
                "client_balance": client_balance,
                "deposit_amount": deposit_amount,
                "withdrawal_amount": withdrawal_amount,
            }
        else:
            balance_map = {
                "client_id": client_id,
                "client_balance": client_balance,
                "deposit_amount": 0.00,
                "withdrawal_amount": 0.00,
            }

        get_client_balance._load_to_database(
            balance_map,
            sqlite="../trading_account/trading_account.sqlite",
            table="client_balance",
        )

        if get_client_balance._close_tabs(0):
            if get_client_balance._close_tabs(0):
                pass
            else:
                get_client_balance.driver.refresh()
        else:
            if get_client_balance._close_tabs(0):
                pass
            else:
                get_client_balance.driver.refresh()


if __name__ == "__main__":
    main()
