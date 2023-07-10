from api_methods import API_METHODS
from processing import BaseProcessing
from selenium.common.exceptions import JavascriptException
import time
from diagnose import (
    age_document_diagnose,
    api_error_diagnose,
    backoffice_filter_diagnose,
    bin_checker_diagnose,
    call_back_failed_diagnose,
    curl_error_diagnose,
    error_comment_diagnose,
    no_comment_diagnose,
    old_bin_checker_diagnose,
    other_queue_diagnose,
    robot_processing_diagnose,
)
import sqlite3
import datetime
import pandas as pd

"""
This is the main class for single_method_analys.py
Mandatory arguments:
    window_size: 'normal' or 'maximize'

method mandatory arguments:
    ps_id: str
    queue: 'Current Transactions' or 'Archive'
    transaction_type: 'Deposit' or 'Withdrawal'

method optional arguments:
    date_from: 'YYYY-MM-DD'
    date_to: 'YYYY-MM-DD'
    transaction_status_code: '1', '2' , '3'
"""


class SingleMethodAnalyse(BaseProcessing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.time = int(time.time())

    def _preparation(self, **kwargs) -> None:
        self._get(url="https://global-cms.fxtm/")
        self._go_to_payments()
        self._go_to_queues(**kwargs)
        self._advance_search(**kwargs)

    def _check_transaction(self, **kwargs):
        time.sleep(30)
        self._remove_comments()
        difference = self._check_current_page_transactions()
        for i in range(100, 100 + 30 * difference, 30):
            time.sleep(1)
            self.transaction = self._get_attribute(i)
            if self.transaction:
                self._checkbox(i)
                self._enter_transaction(self.transaction["transaction_id_url"])
                self.final_transaction = self._transaction_diagnose()
                self._load_to_database(**kwargs)
                time.sleep(2)
                self._close_transaction()
            else:
                pass
        if self._pagination():
            self._next_page()
            return self._check_transaction(**kwargs)
        else:
            pass

    def _load_to_database(self, **kwargs):
        data = pd.DataFrame([self.final_transaction])
        with sqlite3.connect(f"{kwargs.get('db')}") as conn:
            data.to_sql(
                f"{kwargs.get('payment_system')}",
                conn,
                if_exists="append",
                index=False,
            )
            conn.commit()

    def check(self, **kwargs):
        self._preparation(**kwargs)
        self._check_transaction(**kwargs)


class PS356DepositBinChecker(SingleMethodAnalyse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _transaction_diagnose(self, **kwargs):
        time.sleep(2)
        _payment_status = self._payment_status_visibility()
        if not _payment_status:
            self._close_transaction()
            self._enter_transaction(self.transaction["transaction_id_url"])
            self._transaction_diagnose()
        else:
            _transaction_card_issuer_country_name = (
                self._card_issuer_country_name_visibility()
            )
            _register_time = self._get_register_time()
            self.transaction["payment_system_status"] = _payment_status
            self.transaction[
                "card_issuer_country_name"
            ] = _transaction_card_issuer_country_name
            self.transaction["register_time"] = _register_time
            self._another_user()
            if self._comment_visibility():
                self.final_transaction = old_bin_checker_diagnose(
                    self.driver, self.transaction
                )
                print(
                    self.final_transaction["transaction_id"],
                    "--",
                    self.final_transaction["diagnose"],
                    "--",
                    self.final_transaction["card_issuer_country_name"],
                    "--",
                    self.final_transaction["resident_country"],
                    "--",
                    self.final_transaction["register_time"],
                    "--",
                    self.final_transaction["funds_credited_time"],
                    "--",
                    self.final_transaction["processing_time_in_seconds"],
                )
        return self.final_transaction


class PS396DepositBinChecker(SingleMethodAnalyse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _transaction_diagnose(self):
        time.sleep(2)
        _payment_status = self._payment_status_visibility()
        _transaction_card_issuer_country_code = (
            self._card_issuer_country_code_visibility()
        )
        if not _payment_status:
            self._close_transaction()
            self._enter_transaction(self.transaction["transaction_id_url"])
            self._transaction_diagnose()
        else:
            self.transaction["payment_system_status"] = _payment_status
            self.transaction[
                "card_issuer_country_code"
            ] = _transaction_card_issuer_country_code
            self._another_user()
            if self._comment_visibility():
                self.final_transaction = bin_checker_diagnose(
                    self.driver, self.transaction
                )
                print(
                    self.final_transaction["transaction_id"],
                    "--",
                    self.final_transaction["diagnose"],
                    "--",
                    self.final_transaction["source_country"],
                    "--",
                    self.final_transaction["resident_country"],
                    "--",
                    self.final_transaction["country_alpha2"],
                )
        return self.final_transaction


class ManulBoAnalyzier(SingleMethodAnalyse):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _check_transaction(self, **kwargs):
        time.sleep(30)
        self._remove_comments()
        difference = self._check_current_page_transactions()
        for i in range(101, 101 + 31 * difference, 31):
            time.sleep(1)
            self.transaction = self._get_attribute(i)
            if self.transaction:
                self._checkbox(i)
                if self.transaction["method"] in API_METHODS:
                    self._enter_transaction(self.transaction["transaction_id_url"])
                    self.final_transaction = self._transaction_diagnose()
                    self._load_to_database(**kwargs)
                    time.sleep(2)
                    self._close_transaction()
                else:
                    continue
            else:
                pass
        if self._pagination():
            self._next_page()
            return self._check_transaction(**kwargs)
        else:
            pass

    def _comment_diagnose(self, **kwargs):
        if self._comment_visibility():
            try:
                transaction = backoffice_filter_diagnose(self.driver, self.transaction)
            except JavascriptException:
                try:
                    transaction = other_queue_diagnose(self.driver, self.transaction)
                except JavascriptException:
                    try:
                        transaction = curl_error_diagnose(self.driver, self.transaction)
                    except JavascriptException:
                        transaction = robot_processing_diagnose(
                            self.driver, self.transaction
                        )
        return transaction

    def _transaction_diagnose(self, **kwargs):
        time.sleep(2)
        _register_time = self._get_register_time()
        if not _register_time:
            self._close_transaction()
            self._enter_transaction(self.transaction["transaction_id_url"])
            self._transaction_diagnose()
        else:
            _register_time = self._get_register_time()
            self.transaction[
                "payment_system_status"
            ] = self._payment_status_visibility()
            self.transaction["register_time"] = _register_time
            self._another_user()
            self.final_transaction = self._comment_diagnose()
            print(
                self.final_transaction["transaction_id"],
                "--",
                self.final_transaction["diagnose"],
                "--",
                self.final_transaction["register_time"],
                "--",
                self.final_transaction["funds_sent_time"],
                "--",
                self.final_transaction["processing_time_in_seconds"],
            )

        return self.final_transaction
