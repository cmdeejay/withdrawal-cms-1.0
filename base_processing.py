import time
import re
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import JavascriptException
from selenium.webdriver.chrome.service import Service
import sqlite3
from api_methods import API_METHODS, EMAIL_TEMPLATE
from reject_comment import REJECT_COMMENT
from utilities import summary_clean

"""
This is the base class for all cms classes, it has the basic methods for all cms actions. It is based on the selenium chromedriver. 
"""


class BaseProcessing:
    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the class with the selenium chrome driver.
        :optional kwargs:
            - window_size: 'normal', 'max', 'min'.
            - processing: 'True' or 'False'.
            -page: str (how many pages you want to process withdrawal requests.)
        """
        self.ser = Service("driver/chromedriver.exe")
        self.driver_options = webdriver.ChromeOptions()
        self.driver_options.add_experimental_option("detach", True)
        self.driver_options.add_experimental_option(
            "excludeSwitches", ["enable-logging"]
        )
        # self.driver_options.add_argument("--headless=new")
        self.driver_options.add_argument("--disable-extensions")
        self.driver_options.add_argument("--disable-gpu")
        self.driver_options.add_argument("--disable-dev-shm-usage")
        self.driver_options.add_argument("--no-sandbox")
        self.driver_options.add_argument("--disable-infobars")
        self.driver_options.add_argument("--disable-notifications")
        self.driver_options.add_argument("--disable-application-cache")
        self.driver = webdriver.Chrome(service=self.ser, options=self.driver_options)
        if "time" in kwargs:
            self.time = kwargs.get("time")
        if "page" in kwargs:
            self.page = kwargs.get("page")
        else:
            self.page = None
        if "window_size" in kwargs:
            if kwargs["window_size"] == "max":
                self.window_size = "max"
                self.driver.maximize_window()
            elif kwargs["window_size"] == "min":
                self.window_size = "min"
            else:
                self.window_size = "normal"
        else:
            self.window_size = "normal"
        if "processing" in kwargs:
            self.process = kwargs.get("processing")
        else:
            self.process = kwargs.get("processing")
        self.counter = 0
        self.transaction = {}
        self._current_page = 1

    def _get(self, url, *args, **kwargs) -> None:
        """
        This method is used to get to cms.
        :Args:
            - url: str (the url of the cms)
        """
        return self.driver.get(url)

    def _go_to_payments(self) -> None:
        """
        This method is used for driver go to payment page.

        """
        time.sleep(3)
        try:
            self.driver.execute_script(
                "return document.getElementsByTagName('a')[4].click();"
            )
        except JavascriptException:
            self._go_to_payments()

    def _go_to_clients(self, client_id, counter=0) -> None:
        """
        This method is used for driver go to client pages
        """
        time.sleep(3)
        try:
            self.driver.execute_script(
                f"""document.querySelectorAll('input')[1].value = '{client_id}';"""
            )
            self.driver.execute_script(
                """Array.from(document.querySelectorAll('button')).find(el => el.textContent = 'Client ID').click();"""
            )
            return True
        except JavascriptException:
            if counter <= 15:
                return self._go_to_clients(client_id, counter=counter + 1)
            else:
                return False

    def _go_to_filters(self) -> None:
        """
        This method is used for driver go to filters page.

        """
        time.sleep(3)
        try:
            self.driver.execute_script(
                "return document.getElementsByTagName('a')[6].click();"
            )
        except JavascriptException:
            self._go_to_filters()

    def _get_filter_tables(self) -> None:
        time.sleep(3)
        try:
            filter_df = pd.DataFrame()
            for i in range(0, 172):
                table = self.driver.execute_script(
                    f"return document.querySelectorAll('div')[66].children[{i}].innerHTML"
                )
                soup = BeautifulSoup(table, "html.parser")
                table = soup.find("table")
                # Convert the HTML table to a pandas dataframe
                df = pd.read_html(str(table))[0]
                df = df.iloc[[0]]
                filter_df = pd.concat([filter_df, df], axis=0)
            filter_df.columns = [
                "ID",
                "Filter ID",
                "type",
                "Title",
                "Description",
                "filter",
                "Event",
                "Group",
                "Priority",
            ]
            filter_df.reset_index(drop=True, inplace=True)
            print(filter_df)
        except JavascriptException:
            self._get_filter_tables()
        return filter_df

    def _go_to_queues(self, **kwargs) -> None:
        """
        This method is used for driver go to queues page.
        :Kwargs:
            - queue: str (the queue you want to go to)
            - transaction_type: str (the transaction type you want to go to)
        """
        try:
            if kwargs["queue"] != "Current Transactions":
                self.driver.execute_script(
                    f"""Array.from(document.querySelectorAll('button')).find(el => el.textContent === "{kwargs["queue"]}").click();"""
                )
            self.driver.execute_script(
                f"""Array.from(document.querySelectorAll('button')).find(el => el.textContent === "{kwargs["transaction_type"]}").click();"""
            )
            time.sleep(3)
            self.driver.execute_script(
                "Array.from(document.querySelectorAll('div')).find(el => el.textContent === 'Registered').click();"
            )
        except JavascriptException:
            self._go_to_queues(**kwargs)

    def _advance_search(self, **kwargs) -> None:
        time.sleep(15)
        try:
            self.driver.execute_script(
                "Array.from(document.querySelectorAll('button')).find(el => el.textContent === 'Advanced Search').click();"
            )
        except JavascriptException:
            return self._go_to_payment_methods(kwargs)
        try:
            self.driver.execute_script(
                f"Array.from(document.querySelectorAll('input')).filter(el => el.id === 'payment_system')[0].value = {kwargs['ps_id']};"
            )
        except KeyError:
            pass
        try:
            self.driver.execute_script(
                f"Array.from(document.querySelectorAll('input')).filter(el => el.id === 'date_from_3')[0].value = '{kwargs['time_from']}';"
            )
        except KeyError:
            pass
        try:
            self.driver.execute_script(
                f"Array.from(document.querySelectorAll('input')).filter(el => el.id === 'date_to_3')[0].value = '{kwargs['time_to']}';"
            )
        except KeyError:
            pass

        try:
            self.driver.execute_script(
                f"Array.from(document.querySelectorAll('input')).filter(el => el.id === 'status')[0].value = '{kwargs['transaction_status_code']}';"
            )
        except KeyError:
            pass

        time.sleep(5)
        self.driver.execute_script(
            "Array.from(document.querySelectorAll('button')).filter(el => el.textContent === 'Search').slice(-1)[0].click();"
        )
        time.sleep(15)

    def _total_balance(self, counter=0, **kwargs) -> None:
        time.sleep(3)
        try:
            total_balance = self.driver.execute_script(
                """return Array.from(document.querySelectorAll('label')).find(el => el.textContent === 'Total balance:').nextSibling.firstChild.value"""
            )
            if total_balance != "":
                return total_balance
            else: 
                if counter <= 10:
                    return self._total_balance(counter=counter + 1)
                else:
                    return False
        except JavascriptException:
            if counter <= 10:
                return self._total_balance(counter=counter + 1)
            else:
                return False

    def _payments_tab(self, **kwargs) -> None:
        time.sleep(3)
        try:
            self.driver.execute_script(
                """Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Payments')[1].click();"""
            )
        except JavascriptException:
            return self._payments_tab(kwargs)

    def _open_first_transaction(self, counter=0, **kwargs) -> None:
        time.sleep(3)
        try:
            self.driver.execute_script(
                """Array.from(document.querySelectorAll('a')).filter(el => /^[0-9]/.test(el.textContent))[0].click();"""
            )
            return True
        except JavascriptException:
            if counter <= 20:
                return self._open_first_transaction(counter=counter + 1)
            else:
                return False

    def _remove_comments(self) -> None:
        j = self._get_transaction_number()
        try:
            self.driver.execute_script(
                f"""
                function removeDivText() {{for (let i = 108; i <= {108+j*31}; i += 31) {{ document.querySelectorAll('div')[i].textContent = '';}}}}removeDivText();
                """
            )
        except JavascriptException:
            pass
        try:
            self.driver.execute_script(
                f"""
                function removeDivText() {{for (let i = 125; i <= {125+j*31}; i += 31) {{ document.querySelectorAll('div')[i].textContent = '';}}}}removeDivText();
                """
            )
        except JavascriptException:
            pass
        try:
            self.driver.execute_script(
                f"""
                function removeDivText() {{for (let i = 103; i <= {103+j*31}; i += 31) {{ document.querySelectorAll('div')[i].textContent = '';}}}}removeDivText();
                """
            )
        except JavascriptException:
            pass
        try:
            self.driver.execute_script(
                f"""
                function removeDivText() {{for (let i = 117; i <= {117+j*31}; i += 31) {{ document.querySelectorAll('div')[i].textContent = '';}}}}removeDivText();
                """
            )
        except JavascriptException:
            pass
        try:
            self.driver.execute_script(
                f"""
                function removeDivText() {{for (let i = 115; i <= {115+j*31}; i += 31) {{ document.querySelectorAll('div')[i].textContent = '';}}}}removeDivText();
                """
            )
        except JavascriptException:
            pass
        try:
            self.driver.execute_script(
                f"""
                function removeDivText() {{for (let i = 119; i <= {119+j*31}; i += 31) {{ document.querySelectorAll('div')[i].textContent = '';}}}}removeDivText();
                """
            )
        except JavascriptException:
            pass

    def _get_transaction_number(self) -> None:
        transaction_number_from_to = self.driver.execute_script(
            """
            return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'xtb-text').slice(-1)[0].textContent;
            """
        )
        pattern = r"^(\d+)\s*-\s*(\d+)\s*from\s*(\d+)$"

        matches = re.findall(pattern, transaction_number_from_to)
        if matches:
            from_number = int(matches[0][0])
            to_number = int(matches[0][1])
            return to_number - from_number

    def _check_responsible(self, status, *args, **kwargs) -> bool:
        if "BackOffice" in args and "Funds withdrawn" in status:
            return True
        else:
            return False

    def _next_page(self) -> None:
        self.driver.execute_script(
            """Array.from(document.querySelectorAll('button')).filter(el => el.className === ' x-btn-text x-tbar-page-next')[0].click()"""
        )

    def _get_register_time(self, counter=0) -> str:
        time.sleep(1)
        counter += 1
        try:
            register_time = self.driver.execute_script(
                "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Created:')[0].nextSibling.textContent"
            )
            return register_time
        except JavascriptException:
            if counter < 10:
                return self._get_register_time(counter)
            else:
                return False

    def _checkbox(self, i) -> None:
        self.driver.execute_script(
            f"""document.getElementsByTagName('div')[{i-4}].setAttribute('class', 'x-grid3-row x-grid3-row-first x-grid3-row-selected')"""
        )

    def _insert_reject_comment(self, reject_comment) -> None:
        time.sleep(3)
        try:
            self.driver.execute_script(
                f"""Array.from(document.querySelectorAll('textarea')).find(el => el.id.includes('reject_comment_form')).value = '{reject_comment}';"""
            )
        except TypeError:
            return self._insert_reject_comment(self.reject_comment)

    def _reject_process(self, reject_reason) -> bool:
        self.driver.execute_script(
            """Array.from(document.querySelectorAll('button')).find(el => el.textContent === 'Decline').click()"""
        )
        self.reject_comment = REJECT_COMMENT[f"{reject_reason}"]
        self._insert_reject_comment(self.reject_comment)
        # time.sleep(2)
        if self.process:
            self.driver.execute_script(
                """Array.from(document.querySelectorAll('button')).find(el => el.textContent === 'Decline transaction').click();"""
            )
            if self._decline_status():
                return True
            else:
                return False
        else:
            self.driver.execute_script(
                """Array.from(document.querySelectorAll('span')).find(el => el.textContent === 'Transaction processing').previousSibling.click();"""
            )
            return False

    def _another_user(self) -> bool:
        try:
            self.driver.execute_script(
                """Array.from(document.querySelectorAll('button')).filter(el => el.textContent === 'Yes').slice(-1)[0].click();"""
            )
            return True
        except JavascriptException:
            return False

    def _send_withdrawal_pending_email(self):
        time.sleep(1)
        try:
            self.driver.execute_script(
                """Array.from(document.querySelectorAll('img')).filter(el => el.className === 'x-form-trigger x-form-arrow-trigger').slice(-1)[0].click();const y = Array.from(document.querySelectorAll('div')).filter(el => el.textContent === 'Send e-mail')[0];y.click();const x = Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-form-field-wrap x-form-field-trigger-wrap').slice(-1)[0]; x.querySelectorAll('img')[0].click();"""
            )
        except JavascriptException:
            return self._send_withdrawal_pending_email()

        if self._email_template_visibility():
            time.sleep(1)
            if self.process:
                self.driver.execute_script(
                    """Array.from(document.querySelectorAll('button')).filter(el => el.textContent === 'Yes')[0].click();"""
                )
                self.driver.execute_script(
                    """
                    Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-tool x-tool-close').slice(-2)[0].click();
                    """
                )
                return True
            else:
                self.driver.execute_script(
                    """Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-tool x-tool-close')[0].click();Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-tool x-tool-close')[0].click();"""
                )
                return False
        else:
            self.driver.execute_script(
                """Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-tool x-tool-close').slice(-1)[0].click();"""
            )
            return False

    def _email_template_visibility(self, counter=0) -> bool:
        time.sleep(2)
        try:
            self.driver.execute_script(
                f"""Array.from(document.querySelectorAll('span')).filter(el => el.textContent === '{EMAIL_TEMPLATE.get(self.final_transaction['payment_method'])}')[0].click();Array.from(document.querySelectorAll('button')).filter(el => el.textContent === 'Send')[0].click();"""
            )
            return True
        except JavascriptException:
            if counter < 2:
                return self._email_template_visibility(counter=counter + 1)
            else:
                return False

    def _summary_visibility(self, counter=0) -> bool:
        time.sleep(4)
        summary_presence = self.driver.execute_script(
            """return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-viewport').length"""
        )
        if summary_presence >= 4:
            total_str_presence = self.driver.execute_script(
                """return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').slice(-2)[0].textContent"""
            )
            if "Total" in total_str_presence:
                return True
            else:
                counter += 1
                if counter <= 15:
                    return self._summary_visibility()
                else:
                    return False
        else:
            return self._summary_visibility()

    def _decline_status(self, counter=0) -> bool:
        time.sleep(3)
        try:
            decline = self.driver.execute_script(
                """return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Status:')[0].nextSibling.textContent === '[4] Declined';;"""
            )
            if decline:
                return True
        except JavascriptException:
            counter += 1
            if counter <= 10:
                return self._decline_status(counter)
            else:
                return False

    def _payment_status_visibility(self, counter=0) -> str:
        time.sleep(1)
        counter += 1
        try:
            self._payment_system_status = self.driver.execute_script(
                "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Status of Payment system:')[0].nextSibling.textContent;"
            )
            return self._payment_system_status
        except JavascriptException:
            if counter <= 10:
                return self._payment_status_visibility(counter)
            else:
                return False

    def _card_issuer_country_code_visibility(self, counter=0) -> bool:
        time.sleep(1)
        counter += 1
        try:
            self._card_issuer_country_code = self.driver.execute_script(
                "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Client card issuer bank country code:')[0].nextSibling.textContent;"
            )
            return True
        except JavascriptException:
            if counter <= 10:
                return self._card_issuer_visibility(counter)
            else:
                return False

    def _card_issuer_country_name_visibility(self, counter=0) -> bool:
        time.sleep(1)
        counter += 1
        try:
            self._card_issuer_country_name = self.driver.execute_script(
                "return Array.from(document.querySelectorAll('li')).filter(el => el.textContent.includes(' card_issuer_country_name')).slice(-1)[0].textContent"
            )
            self._card_issuer_country_name = self._card_issuer_country_name.split("-")[
                -1
            ]
            self._card_issuer_country_name = self._card_issuer_country_name.strip()
            return self._card_issuer_country_name
        except JavascriptException:
            if counter <= 10:
                return self._card_issuer_country_name_visibility(counter)
            else:
                return False

    def _b2binpay_name_visibility(self, counter=0) -> bool:
        time.sleep(1)
        counter += 1
        try:
            self._name = self.driver.execute_script(
                "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Payment system name: ')[0].nextSibling.textContent;"
            )
            return True
        except JavascriptException:
            if counter <= 10:
                return self._b2binpay_name_visibility(counter)
            else:
                return False

    def _comment_visibility(self, counter=0) -> bool:
        time.sleep(2)
        counter += 1
        try:
            self.driver.execute_script(
                "Array.from(document.querySelectorAll('div')).find(el => el.className === 'x-grid3-cell-inner x-grid3-col-0').textContent;"
            )
            return True
        except JavascriptException:
            if counter <= 10:
                return self._comment_visibility(counter)
            else:
                return False

    def _summary_total(self) -> None:
        self.driver.execute_script(
            "Array.from(document.querySelectorAll('button')).filter(el => el.textContent === 'Summary')[0].click();"
        )
        if self._summary_visibility():
            self.summary_text = self.driver.execute_script(
                """return Array.from(Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').slice(-2)[0].getElementsByTagName('td')).map(x => x.textContent).filter(x => (x || "").trim()).join(";");"""
            )
            self.first_row = summary_clean(self.summary_text).iloc[0]
            deposit_usd = self.first_row["Deposit USD"]
            withdrawal_usd = self.first_row["Withdrawal USD"]

            transfer_volume = {
                "Deposit USD": deposit_usd,
                "Withdrawal USD": withdrawal_usd,
            }
            self.driver.execute_script(
                "Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-window-header x-window-header-noborder x-unselectable x-window-draggable')[0].firstElementChild.click();"
            )
            return transfer_volume
        else:
            print("summary is not visible")

    def _summary_diagnose(self) -> None:
        self.driver.execute_script(
            "Array.from(document.querySelectorAll('button')).filter(el => el.textContent === 'Summary')[0].click();"
        )
        if self._summary_visibility():
            self.summary_text = self.driver.execute_script(
                """return Array.from(Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').slice(-2)[0].getElementsByTagName('td')).map(x => x.textContent).filter(x => (x || "").trim()).join(";");"""
            )
            self.clean_summary = summary_clean(self.summary_text)
            print()
            print(self.clean_summary)
            print()
            self.driver.execute_script(
                "Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-window-header x-window-header-noborder x-unselectable x-window-draggable')[0].firstElementChild.click();"
            )
        else:
            print("summary is not visible")

    def _check_current_page_transactions(self):
        pattern = r"(\d+)\s*-\s*(\d+)\s*from\s*(\d+)"
        string = self.driver.execute_script(
            "return Array.from(document.querySelectorAll('div')).filter(el => el.textContent.includes('from')).slice(-1)[0].textContent;"
        )
        match = re.search(pattern, string)

        if match:
            first_num = int(match.group(1))
            second_num = int(match.group(2))
            difference = second_num - first_num + 1
            return difference

    def _close_transaction(self):
        self.driver.execute_script("document.getElementsByTagName('a')[22].click();")

    def _enter_transaction(self, *args, **kwargs):
        """
        manual process diagnose,
        doc not provided diagnose,
        doc not requested diagnose
        """
        self.counter += 1
        self.driver.execute_script("arguments[0].click();", args[0])

    def _get_attribute(self, i) -> dict:
        try:
            self._method = self.driver.execute_script(
                f"return document.getElementsByTagName('div')[{i}].textContent;"
            )
            self._take_process = self.driver.execute_script(
                f"return document.getElementsByTagName('div')[{i+4}].textContent;"
            )
            self._give_process = self.driver.execute_script(
                f"return document.getElementsByTagName('div')[{i+5}].textContent;"
            )
            self._status = self.driver.execute_script(
                f"return document.getElementsByTagName('div')[{i+6}].textContent;"
            )
            self._transaction_id_url = self.driver.execute_script(
                f"return document.getElementsByTagName('div')[{i-1}].firstElementChild;"
            )
            self._transaction_id = self.driver.execute_script(
                f"return document.getElementsByTagName('div')[{i-1}].firstElementChild.textContent;"
            )
            transaction = {
                "transaction_id_url": self._transaction_id_url,
                "transaction_id": self._transaction_id,
                "method": self._method,
                "take_process": self._take_process,
                "give_process": self._give_process,
                "status": self._status,
            }

            if i == 100 and self._current_page == 1:
                self.withdrawal_report = pd.DataFrame()
            return transaction
        except JavascriptException:
            return False

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
                    self.transaction["take_process"],
                )
                self._checkbox(i)
                if self.transaction["method"] in API_METHODS and _responsible:
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
    
    def _close_tabs(self, tab_id):
        time.sleep(1)
        try:
            self.driver.execute_script(
                f"""Array.from(document.querySelectorAll('a')).filter(el => el.className === 'x-tab-strip-close')[{tab_id}].click();"""
            )
            return True
        except JavascriptException:
            self._close_tabs(tab_id)

    def _pagination(self, *args, **kwargs) -> bool:
        self._current_page = self.driver.execute_script(
            """return Array.from(document.querySelectorAll('input')).filter(el => el.className === 'x-form-text x-form-field x-form-num-field x-tbar-page-number')[0].value"""
        )
        if self.page is not None:
            self._total_page = self.page
        else:
            self._from_total_page = self.driver.execute_script(
                """return Array.from(document.querySelectorAll('div')).filter(el => el.textContent.includes('from')).slice(-2)[0].textContent"""
            )
            self._total_page = self._from_total_page.split()
            number_part = self._total_page[-1].strip()
            self._total_page = int(number_part)
        print(int(self._current_page) + 1, self._total_page)
        if int(self._current_page) < self._total_page:
            return True
        else:
            return False

    def _go_to_transaction(self, transaction_id):
        time.sleep(1)
        self.driver.execute_script(
            f"Array.from(document.querySelectorAll('input')).filter(el => el.className === ' x-form-text x-form-field x-form-num-field')[1].value = {transaction_id};"
        )
        self.driver.execute_script(
            "Array.from(document.querySelectorAll('button')).find(el => el.textContent === 'Transfer ID').click()"
        )

    def _action(self, transaction):
        # if transaction["action"] == "Decline":
        if (
            transaction["diagnose"] == "Rejected comment detected"
            or transaction["diagnose"] == "Insufficient funds"
        ):
            if self._reject_process(reject_reason=transaction["diagnose"]):
                transaction["action_done"] = "True"
            else:
                transaction["action_done"] = "False"
        elif transaction["action"] == "Check_process_condition":
            self._summary_diagnose()
        elif transaction["action"] == "Send email":
            if self._send_withdrawal_pending_email():
                transaction["action_done"] = "True"
            else:
                transaction["action_done"] = "False"
        print(
            transaction["transaction_id"],
            "--",
            transaction["status"],
            "--",
            transaction["diagnose"],
        )

    def _load_to_database(self, **kwargs):
        """
        Append Pandas DataFrame to SQLite table, automatically creating missing columns.
        """
        table_name = kwargs.get("table_name")

        data = pd.DataFrame([self.final_transaction])
        # create connection to SQLite database
        with sqlite3.connect(f"{kwargs.get('db')}") as conn:
            # get columns in DataFrame
            data_cols = data.columns.tolist()

            # check if table exists in SQLite database
            table_exists = pd.read_sql_query(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'",
                conn,
            )

            # if table exists, get columns in the table
            if not table_exists.empty:
                table_cols = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
                table_cols = table_cols["name"].tolist()
            else:
                table_cols = []

            # create new columns in SQLite table
            new_cols = [col for col in data_cols if col not in table_cols]
            for col in new_cols:
                try:
                    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} text")
                except:
                    pass

            # append DataFrame data to SQLite table
            data.to_sql(name=table_name, con=conn, if_exists="append", index=False)

            # close connection to SQLite database

    def _filter_load_to_database(self, **kwargs):
        """
        Append Pandas DataFrame to SQLite table, automatically creating missing columns.
        """
        table_name = kwargs.get("table_name")

        data = self.filter_df

        # create connection to SQLite database
        with sqlite3.connect(f"{kwargs.get('db')}") as conn:
            # get columns in DataFrame
            data_cols = data.columns.tolist()

            # check if table exists in SQLite database
            table_exists = pd.read_sql_query(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'",
                conn,
            )

            # if table exists, get columns in the table
            if not table_exists.empty:
                table_cols = pd.read_sql_query(f"PRAGMA table_info({table_name})", conn)
                table_cols = table_cols["name"].tolist()
            else:
                table_cols = []

            # create new columns in SQLite table
            new_cols = [col for col in data_cols if col not in table_cols]
            for col in new_cols:
                try:
                    conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} text")
                except:
                    pass

            # append DataFrame data to SQLite table
            data.to_sql(name=table_name, con=conn, if_exists="append", index=False)

            # close connection to SQLite database
