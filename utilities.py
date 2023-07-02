import re
import time

import pandas as pd
import requests


def summary_clean(summary_text):
    split_text = re.split(r"[;](?=[A-Z])|[;](?=[1-9][A-Z])", summary_text)
    a = []
    for x in split_text:
        a.append(x.split(";"))

    df = pd.DataFrame(
        a,
        columns=[
            "Payment System",
            "Deposit USD",
            "Withdrawal USD",
            "Net USD",
            "Allowed USD",
        ],
    )
    return df


def ip_checker(ip, counter=0):
    counter += 1
    response = requests.get(f"https://ipapi.co/{ip}/json/")
    if response.ok:
        return response.json()
    elif counter < 5:
        time.sleep(3)
        return ip_checker(ip, counter)
    else:
        return None
