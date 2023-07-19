import time

from selenium.common.exceptions import JavascriptException

from api_methods import API_METHODS
from base_processing import BaseProcessing
from diagnose import (
    age_document_diagnose,
    api_error_diagnose,
    blacklist_diagnose,
    call_back_failed_diagnose,
    curl_error_diagnose,
    doc_not_provided_diagnose,
    doc_not_requested_diagnose,
    error_comment_diagnose,
    free_margin_diagnose,
    low_balance_diagnose,
    manual_process_diagnose,
    reject_comment_diagnose,
    sla_violation_diagnose,
    b2binpay_processing_error_diagnose,
    b2binpay_more_than_deposit_diagnose,
    b2binpay_no_deposit_diagnose,
    b2binpay_minimum_amount_diagnose,
    b2binpay_account_in_use_by_other_diagnose,
    credit_diagnose,
    no_comment_diagnose,
    backoffice_filter_diagnose,
)


class Status2Processing(BaseProcessing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _preparation(self, **kwargs) -> None:
        self._get(url="https://global-cms.fxtm/")
        self._go_to_payments()
        self._go_to_queues(**kwargs)

    def _comment_diagnose(self):
        if self._comment_visibility():
            if "Not Approved" in self.transaction["payment_system_status"]:
                try:
                    transaction = doc_not_provided_diagnose(
                        self.driver, self.transaction
                    )
                except (JavascriptException, ValueError):
                    transaction = doc_not_requested_diagnose(self.transaction)
            else:
                try:
                    transaction = call_back_failed_diagnose(
                        self.driver, self.transaction
                    )
                except JavascriptException:
                    try:
                        transaction = reject_comment_diagnose(
                            self.driver, self.transaction
                        )
                    except JavascriptException:
                        try:
                            transaction = curl_error_diagnose(
                                self.driver, self.transaction
                            )
                        except JavascriptException:
                            try:
                                transaction = low_balance_diagnose(
                                    self.driver, self.transaction
                                )
                            except JavascriptException:
                                try:
                                    transaction = error_comment_diagnose(
                                        self.driver, self.transaction
                                    )
                                except JavascriptException:
                                    try:
                                        transaction = age_document_diagnose(
                                            self.driver, self.transaction
                                        )
                                    except JavascriptException:
                                        try:
                                            transaction = api_error_diagnose(
                                                self.driver, self.transaction
                                            )
                                        except JavascriptException:
                                            transaction = sla_violation_diagnose(
                                                self.register_time, self.transaction
                                            )
        return transaction

    def _transaction_diagnose(self):
        time.sleep(2)
        _payment_status = self._payment_status_visibility()
        if not _payment_status:
            self._close_transaction()
            self._enter_transaction(self.transaction["transaction_id_url"])
            self._transaction_diagnose()
        else:
            self.transaction["payment_system_status"] = _payment_status
            self._another_user()
            self.register_time = self._get_register_time()
            transaction_or_bool = manual_process_diagnose(self.driver, self.transaction)
            blacklist_or_bool = blacklist_diagnose(self.driver, self.transaction)
            if transaction_or_bool:
                self.final_transaction = transaction_or_bool
            elif blacklist_or_bool:
                self.final_transaction = blacklist_or_bool
            else:
                self.final_transaction = self._comment_diagnose()
        return self.final_transaction

    def _b2binpay_comment_diagnose(self):
        if self._comment_visibility():
            try:
                transaction = api_error_diagnose(self.driver, self.transaction)
            except JavascriptException:
                try:
                    transaction = b2binpay_processing_error_diagnose(
                        self.driver, self.transaction
                    )
                except JavascriptException:
                    try:
                        transaction = b2binpay_more_than_deposit_diagnose(
                            self.driver, self.transaction
                        )
                    except JavascriptException:
                        try:
                            transaction = b2binpay_minimum_amount_diagnose(
                                self.driver, self.transaction
                            )
                        except JavascriptException:
                            try:
                                transaction = b2binpay_no_deposit_diagnose(
                                    self.driver, self.transaction
                                )
                            except JavascriptException:
                                try:
                                    transaction = (
                                        b2binpay_account_in_use_by_other_diagnose(
                                            self.driver, self.transaction
                                        )
                                    )
                                except JavascriptException:
                                    transaction = sla_violation_diagnose(
                                        self.register_time, self.transaction
                                    )
        return transaction

    def _b2binpay_diagnose(self):
        time.sleep(2)
        _b2binpay_name = self._b2binpay_name_visibility()
        if not _b2binpay_name:
            self._close_transaction()
            self._enter_transaction(self.transaction["transaction_id_url"])
            self._b2binpay_diagnose()
        else:
            self.transaction["payment_system_status"] = "N/A"
            self._another_user()
            self.register_time = self._get_register_time()
            blacklist_or_bool = blacklist_diagnose(self.driver, self.transaction)
            if blacklist_or_bool:
                self.final_transaction = blacklist_or_bool
            else:
                self.final_transaction = self._b2binpay_comment_diagnose()
        return self.final_transaction

    def _check_transaction(self, **kwargs):
        time.sleep(8)
        self._remove_comments()
        difference = self._check_current_page_transactions()
        for i in range(101, 101 + 31 * difference, 31):
            time.sleep(1)
            self.transaction = self._get_attribute(i)
            if self.transaction:
                _responsible = self._check_responsible(
                    self.transaction["status"],
                    self.transaction["give_process"],
                )
                self._checkbox(i)
                if self.transaction["method"] == "B2BInPay GPS (-)" and _responsible:
                    self._enter_transaction(self.transaction["transaction_id_url"])
                    self.final_transaction = self._b2binpay_diagnose()
                    self._action(self.final_transaction)
                    time.sleep(2)
                    self._close_transaction()
                elif (
                    self.transaction["method"] in API_METHODS
                    and self.transaction["method"] != "B2BInPay GPS (-)"
                    and _responsible
                ):
                    self._enter_transaction(self.transaction["transaction_id_url"])
                    self.final_transaction = self._transaction_diagnose()
                    self._action(self.final_transaction)
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

    def start_processing(self, **kwargs) -> None:
        self._preparation(**kwargs)
        time.sleep(8)
        self._check_transaction(**kwargs)


class Status1Processing(BaseProcessing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _preparation(self, **kwargs) -> None:
        self._get(url="https://global-cms.fxtm/")
        self._go_to_payments()
        self._go_to_queues(**kwargs)

    def _check_responsible(self, status, *args, **kwargs) -> bool:
        if "BackOffice" in args and "Processing" in status:
            return True
        else:
            return False

    def _comment_diagnose(self):
        if not self._comment_visibility():
            if "Not Approved" in self.transaction["payment_system_status"]:
                transaction = doc_not_requested_diagnose(self.transaction)
            else:
                transaction = sla_violation_diagnose(
                    self.register_time, self.transaction
                )
        else:
            if "Not Approved" in self.transaction["payment_system_status"]:
                try:
                    transaction = credit_diagnose(self.driver, self.transaction)
                except JavascriptException:
                    try:
                        transaction = doc_not_provided_diagnose(
                            self.driver, self.transaction
                        )
                    except (JavascriptException, ValueError, TypeError):
                        transaction = doc_not_requested_diagnose(self.transaction)
            else:
                try:
                    transaction = credit_diagnose(self.driver, self.transaction)
                except JavascriptException:
                    transaction = sla_violation_diagnose(
                        self.register_time, self.transaction
                    )
        return transaction

    def _transaction_diagnose(self):
        time.sleep(2)
        _payment_status = self._payment_status_visibility()
        if not _payment_status and self.transaction["method"] != "B2BInPay GPS (-)":
            self._close_transaction()
            self._enter_transaction(self.transaction["transaction_id_url"])
            self._transaction_diagnose()
        else:
            self.transaction["payment_system_status"] = _payment_status
            self._another_user()
            self.register_time = self._get_register_time()
            no_free_margin_or_bool = free_margin_diagnose(self.driver, self.transaction)
            blacklist_or_bool = blacklist_diagnose(self.driver, self.transaction)
            if no_free_margin_or_bool:
                self.final_transaction = no_free_margin_or_bool
            elif blacklist_or_bool:
                self.final_transaction = blacklist_or_bool
            else:
                self.final_transaction = self._comment_diagnose()
        return self.final_transaction

    def start_processing(self, **kwargs):
        self._preparation(**kwargs)
        time.sleep(8)
        self._check_transaction(**kwargs)


class FilterStatus1Processing(Status1Processing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _comment_diagnose(self):
        if not self._comment_visibility():
            transaction = no_comment_diagnose(self.driver, self.transaction)
        else:
            try:
                transaction = backoffice_filter_diagnose(self.driver, self.transaction)
            except JavascriptException:
                transaction = no_comment_diagnose(self.driver, self.transaction)
        return transaction

    def _transaction_diagnose(self):
        time.sleep(2)
        _payment_status = self._payment_status_visibility()
        if not _payment_status and self.transaction["method"] != "B2BInPay GPS (-)":
            self._close_transaction()
            self._enter_transaction(self.transaction["transaction_id_url"])
            self._transaction_diagnose()
        else:
            self.transaction["payment_system_status"] = _payment_status
            self._another_user()
            self.final_transaction = self._comment_diagnose()
        return self.final_transaction


class FilterStatus2Processing(Status2Processing):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _comment_diagnose(self):
        if self._comment_visibility():
            try:
                transaction = age_document_diagnose(self.driver, self.transaction)
            except JavascriptException:
                try:
                    transaction = backoffice_filter_diagnose(
                        self.driver, self.transaction
                    )
                except JavascriptException:
                    try:
                        transaction = api_error_diagnose(self.driver, self.transaction)
                    except JavascriptException:
                        try:
                            transaction = curl_error_diagnose(
                                self.driver, self.transaction
                            )
                        except JavascriptException:
                            try:
                                transaction = error_comment_diagnose(
                                    self.driver, self.transaction
                                )
                            except JavascriptException:
                                try:
                                    transaction = call_back_failed_diagnose(
                                        self.driver, self.transaction
                                    )
                                except JavascriptException:
                                    transaction = no_comment_diagnose(
                                        self.driver, self.transaction
                                    )
        return transaction

    def _transaction_diagnose(self):
        time.sleep(2)
        _payment_status = self._payment_status_visibility()
        if not _payment_status and self.transaction["method"] != "B2BInPay GPS (-)":
            self._close_transaction()
            self._enter_transaction(self.transaction["transaction_id_url"])
            self._transaction_diagnose()
        else:
            self.transaction["payment_system_status"] = _payment_status
            self._another_user()
            self.final_transaction = self._comment_diagnose()
        return self.final_transaction

    def _check_transaction(self):
        time.sleep(8)
        self._remove_comments()
        for i in range(100, 3100, 30):
            time.sleep(1)
            self.transaction = self._get_attribute(i)
            if self.transaction:
                _responsible = self._check_responsible(
                    self.transaction["status"],
                    self.transaction["give_process"],
                )
                self._checkbox(i)
                if self.transaction["method"] in API_METHODS and _responsible:
                    self._enter_transaction(self.transaction["transaction_id_url"])
                    self.final_transaction = self._transaction_diagnose()
                    self._action(self.final_transaction)
                    time.sleep(2)
                    self._close_transaction()
                else:
                    continue
            else:
                return self.withdrawal_report
        if self._pagination():
            self._next_page()
            return self._check_transaction()
        else:
            return self.withdrawal_report
