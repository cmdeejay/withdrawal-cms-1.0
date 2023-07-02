import re
import pycountry
from selenium.common.exceptions import JavascriptException

from country_list import RESTRICTED_COUNTRIES
from time_operation import (
    comment_time_compare,
    manual_bo_register_time_and_funds_sent_difference,
    register_time_sla_violation,
    reminder_time,
    violation_delta,
    ps356_register_time_and_funds_credited_difference,
    waiting_bo_time_difference,
)
from transaction import Transaction
from utilities import ip_checker


def manual_process_diagnose(driver, this_transaction):
    try:
        _manual_processing = driver.execute_script(
            "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Transaction id:')[0].nextSibling.textContent"
        )
        transaction = Transaction(
            transaction_id=this_transaction["transaction_id"],
            payment_method=this_transaction["method"],
            take_process=this_transaction["take_process"],
            give_process=this_transaction["give_process"],
            status=this_transaction["status"],
            payment_system_status=this_transaction["payment_system_status"],
            diagnose=f"Processed, Transaction id: {_manual_processing}",
            action="Check psp portal",
            action_done="False",
        )
        return transaction.__dict__
    except JavascriptException:
        return False


def doc_not_provided_diagnose(driver, this_transaction):
    _last_doc_comment = driver.execute_script(
        """return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('cup') || x.textContent.includes('req')|| x.textContent.includes('Email sent') || x.textContent.includes('Auto e-mail: Withdrawal pending, online banking confirmation requested'))[15].textContent"""
    )

    _first_doc_comment = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('cup') || x.textContent.includes('req')|| x.textContent.includes('Email sent') || x.textContent.includes('Auto e-mail: Withdrawal pending, online banking confirmation requested')).slice(-2)[0].textContent"
    )
    if "Client had no trading activity" in _first_doc_comment:
        _first_doc_comment = driver.execute_script(
            "return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('cup') || x.textContent.includes('req')|| x.textContent.includes('Email sent') || x.textContent.includes('Auto e-mail: Withdrawal pending, online banking confirmation requested')).slice(-4)[0].textContent"
        )
        if "Client had no trading activity" in _first_doc_comment:
            _first_doc_comment = driver.execute_script(
                "return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('cup') || x.textContent.includes('req')|| x.textContent.includes('Email sent') || x.textContent.includes('Auto e-mail: Withdrawal pending, online banking confirmation requested')).slice(-6)[0].textContent"
            )

    if "PE" not in _first_doc_comment and "PE" not in _last_doc_comment:
        _last_doc_req = driver.execute_script(
            """return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('cup') || x.textContent.includes('req')|| x.textContent.includes('Email sent') || x.textContent.includes('Auto e-mail: Withdrawal pending, online banking confirmation requested'))[15].textContent.substring(0,16);"""
        )

        _first_doc_req = driver.execute_script(
            "return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('cup') || x.textContent.includes('req')|| x.textContent.includes('Email sent') || x.textContent.includes('Auto e-mail: Withdrawal pending, online banking confirmation requested')).slice(-2)[0].textContent.substring(0,16);"
        )

    elif "PE" in _first_doc_comment and "PE" not in _last_doc_comment:
        _last_doc_req = driver.execute_script(
            """return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('cup') || x.textContent.includes('req')|| x.textContent.includes('Email sent') || x.textContent.includes('Auto e-mail: Withdrawal pending, online banking confirmation requested'))[15].textContent.substring(0,16);"""
        )

        _first_doc_req = driver.execute_script(
            "return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('cup') || x.textContent.includes('req')|| x.textContent.includes('Email sent') || x.textContent.includes('Auto e-mail: Withdrawal pending, online banking confirmation requested')).slice(-4)[0].textContent.substring(0,16);"
        )

    else:
        _first_doc_req = driver.execute_script(
            "return Array.from(document.querySelectorAll('div')).find( x => x.textContent.includes('I made this up, it is impossible to find!'))"
        )

        _last_doc_req = driver.execute_script(
            """return Array.from(document.querySelectorAll('div')).find( x => x.textContent.includes('I made this up, it is impossible to find!'));"""
        )

    _time_to_remind = reminder_time(_last_doc_req)

    if comment_time_compare(_first_doc_req):
        if _time_to_remind:
            transaction = Transaction(
                transaction_id=this_transaction["transaction_id"],
                payment_method=this_transaction["method"],
                take_process=this_transaction["take_process"],
                give_process=this_transaction["give_process"],
                status=this_transaction["status"],
                payment_system_status=this_transaction["payment_system_status"],
                diagnose=f"Doc not provided, within 24h, send reminder in {_time_to_remind}",
                action="Send reminder",
                action_done="False",
                doc_req_over_24h="False",
            )
        else:
            transaction = Transaction(
                transaction_id=this_transaction["transaction_id"],
                payment_method=this_transaction["method"],
                take_process=this_transaction["take_process"],
                give_process=this_transaction["give_process"],
                status=this_transaction["status"],
                payment_system_status=this_transaction["payment_system_status"],
                diagnose=f"Doc not provided, within 24h, send reminder now",
                action="Send email",
                action_done="False",
                doc_req_over_24h="False",
            )
    else:
        transaction = Transaction(
            transaction_id=this_transaction["transaction_id"],
            payment_method=this_transaction["method"],
            take_process=this_transaction["take_process"],
            give_process=this_transaction["give_process"],
            status=this_transaction["status"],
            payment_system_status=this_transaction["payment_system_status"],
            diagnose="Doc not provided, over 24h",
            action="Decline",
            action_done="False",
            doc_req_over_24h="True",
        )
    return transaction.__dict__


def doc_not_requested_diagnose(this_transaction):
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="Doc not requested",
        action="Send email",
        action_done="False",
    )
    return transaction.__dict__


def call_back_failed_diagnose(driver, this_transaction):
    error_comment = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('FAILED') || el.textContent.includes('Failed'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="Call back failed",
        action="Manual",
        action_done="False",
    )
    return transaction.__dict__


def reject_comment_diagnose(driver, this_transaction):
    reject_comment = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('Rejected') || el.textContent.includes('Withdrawal request was rejected') || el.textContent.includes('Request has been NOT processed by Paytrust88.'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="Rejected comment detected",
        action="Decline",
        action_done="False",
    )
    return transaction.__dict__


def low_balance_diagnose(driver, this_transaction):
    error_comment = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('Low balance') || el.textContent.includes('low balance'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="Low balance detected",
        action="Manual",
        action_done="False",
    )
    return transaction.__dict__


def error_comment_diagnose(driver, this_transaction):
    error_comment = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('Error') || el.textContent.includes('Response contains error: '))[0].textContent"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="Error detected",
        action="Manual",
        action_done="False",
    )
    return transaction.__dict__


def age_document_diagnose(driver, this_transaction):
    error_comment = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('OCR Client'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="Check age documents",
        action="Manual",
        action_done="False",
    )
    return transaction.__dict__


def api_error_diagnose(driver, this_transaction):
    error_comment = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('Client error') || el.textContent.includes('Server error'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="API error detected",
        action="Manual",
        action_done="False",
    )
    return transaction.__dict__


def curl_error_diagnose(driver, this_transaction):
    filters_and_condition = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.textContent.includes('cURL error') || el.textContent.includes('Failed p2p withdrawal')).slice(-1)[0].textContent;"
    )
    funds_sent_time = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.textContent.includes('Being processed by external payment system') || el.textContent.includes('Funds sent') || el.textContent.includes('Declined')).slice(-2)[0].textContent.substring(0,19);"
    )
    processing_time_in_seconds = manual_bo_register_time_and_funds_sent_difference(
        this_transaction["register_time"], funds_sent_time
    )

    move_to_bo_time = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.textContent.includes('cURL error') || el.textContent.includes('Failed p2p withdrawal')).slice(-2)[0].textContent.substring(0,19);"
    )
    waiting_bo_time_in_seconds = waiting_bo_time_difference(
        move_to_bo_time, funds_sent_time
    )

    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        register_time=this_transaction["register_time"],
        move_to_bo_time=move_to_bo_time,
        funds_sent_time=funds_sent_time,
        processing_time_in_seconds=processing_time_in_seconds,
        waiting_bo_time_in_seconds=waiting_bo_time_in_seconds,
        payment_system_status=this_transaction["payment_system_status"],
        diagnose=filters_and_condition,
        action="N/A",
        action_done="N/A",
    )
    return transaction.__dict__


def sla_violation_diagnose(register_time, this_transaction):
    if register_time_sla_violation(register_time):
        transaction = Transaction(
            transaction_id=this_transaction["transaction_id"],
            payment_method=this_transaction["method"],
            take_process=this_transaction["take_process"],
            give_process=this_transaction["give_process"],
            status=this_transaction["status"],
            sla_violation="True",
            payment_system_status=this_transaction["payment_system_status"],
            diagnose="SLA violation",
            action="Check_process_condition",
            action_done="False",
        )
    else:
        time_to_violation = violation_delta(register_time)
        transaction = Transaction(
            transaction_id=this_transaction["transaction_id"],
            payment_method=this_transaction["method"],
            take_process=this_transaction["take_process"],
            give_process=this_transaction["give_process"],
            status=this_transaction["status"],
            sla_violation="False",
            payment_system_status=this_transaction["payment_system_status"],
            diagnose=f"No error found, time to SLA violation {time_to_violation}",
            action="Check_process_condition",
            action_done="False",
        )
    return transaction.__dict__


def blacklist_diagnose(driver, this_transaction):
    try:
        _blacklist_comment = driver.execute_script(
            "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Reason for BO Blacklist: ')[0].nextSibling.textContent"
        )
        transaction = Transaction(
            transaction_id=this_transaction["transaction_id"],
            payment_method=this_transaction["method"],
            take_process=this_transaction["take_process"],
            give_process=this_transaction["give_process"],
            status=this_transaction["status"],
            payment_system_status=this_transaction["payment_system_status"],
            diagnose=f"blacklist comment:{_blacklist_comment}",
            blacklist="True",
            action="Manual",
            action_done="False",
        )
        return transaction.__dict__
    except JavascriptException:
        return False


def ip_violation_diagnose(driver, this_transaction):
    try:
        _ip_address = driver.execute_script(
            "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'IP:')[0].nextSibling.textContent"
        )
        try:
            _ip_country = re.search(r"\((.*?)\)", _ip_address).group(1)
        except AttributeError:
            _ip_address = _ip_address.strip()
            response = ip_checker(_ip_address)
            if response is not None:
                try:
                    _ip_country = response["country_name"].upper()
                except KeyError:
                    _ip_country = "UNKNOWN"
            else:
                _ip_country = "UNKNOWN"
        if _ip_country in RESTRICTED_COUNTRIES:
            transaction = Transaction(
                transaction_id=this_transaction["transaction_id"],
                payment_method=this_transaction["method"],
                take_process=this_transaction["take_process"],
                give_process=this_transaction["give_process"],
                status=this_transaction["status"],
                payment_system_status=this_transaction["payment_system_status"],
                diagnose=f"Restricted country: {_ip_country}",
                ip_violation="True",
                action="send IP explanation email",
                action_done="False",
            )
            return transaction.__dict__
        else:
            return False
    except JavascriptException:
        return False


def free_margin_diagnose(driver, this_transaction):
    try:
        _amount1 = driver.execute_script(
            "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Amount_1:')[0].nextSibling.textContent"
        )

        _amount1 = float(re.search(r"\[(.*?)\]", _amount1).group(1))
        try:
            _free_margin = driver.execute_script(
                "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Free margin: ')[0].nextSibling.textContent"
            )
        except JavascriptException:
            _free_margin = driver.execute_script(
                "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Balance: ')[0].nextSibling.textContent"
            )
        _free_margin = int("".join(filter(str.isdigit, _free_margin)))
        _free_margin = f"{_free_margin / 100:.2f}"
        _free_margin = float(_free_margin)

        if _free_margin < _amount1:
            transaction = Transaction(
                transaction_id=this_transaction["transaction_id"],
                payment_method=this_transaction["method"],
                take_process=this_transaction["take_process"],
                give_process=this_transaction["give_process"],
                status=this_transaction["status"],
                payment_system_status=this_transaction["payment_system_status"],
                diagnose=f"Insufficient funds",
                free_margin_violation="True",
                action="Decline",
                action_done="False",
            )
            return transaction.__dict__
        else:
            return False
    except JavascriptException:
        return False


def bin_checker_diagnose(driver, this_transaction):
    try:
        bin_checker_comment = driver.execute_script(
            "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('BIN does not match'))[0].textContent;"
        )
        diagnose = "Bin does not match"
    except JavascriptException:
        diagnose = "Bin is matching with client country"

    resident_country = driver.execute_script(
        "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Country: ')[0].nextSibling.textContent;"
    )
    # split the string at the hyphen
    parts = resident_country.split("-")
    country_part = parts[1].strip()
    country_name = country_part.split(",")[0]
    try:
        country = pycountry.countries.get(name=country_name)
        country_alpha2 = country.alpha_2
    except AttributeError:
        country_alpha2 = "Unknown"

    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose=diagnose,
        card_issuer_country_code=this_transaction["card_issuer_country_code"],
        resident_country=country_name,
        country_alpha2=country_alpha2,
    )

    return transaction.__dict__


def old_bin_checker_diagnose(driver, this_transaction):
    try:
        bin_checker_comment = driver.execute_script(
            "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('BIN country different from client country'))[0].textContent;"
        )
        diagnose = "Bin checker detected different country"
    except JavascriptException:
        diagnose = "Bin checker did not detect different country"

    resident_country = driver.execute_script(
        "return Array.from(document.querySelectorAll('span')).filter(el => el.textContent === 'Country: ')[0].nextSibling.textContent;"
    )
    funds_credited_time = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.textContent.includes('Deposit PRX') || el.textContent.includes('deposit PRX')).slice(-2)[0].textContent.substring(0,19);"
    )
    processing_time_in_seconds = ps356_register_time_and_funds_credited_difference(
        this_transaction["register_time"], funds_credited_time
    )
    # split the string at the hyphen
    parts = resident_country.split("-")
    country_part = parts[1].strip()
    country_name = country_part.split(",")[0]

    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        register_time=this_transaction["register_time"],
        funds_credited_time=funds_credited_time,
        processing_time_in_seconds=processing_time_in_seconds,
        diagnose=diagnose,
        card_issuer_country_name=this_transaction["card_issuer_country_name"],
        resident_country=country_name,
    )

    return transaction.__dict__


def credit_diagnose(driver, this_transaction):
    credit_error = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('	Transaction reaches credit boundary'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="credit removal",
        action="remove credit",
        action_done="False",
    )
    return transaction.__dict__


def b2binpay_processing_error_diagnose(driver, this_transaction):
    processing_error = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('Being processed by external payment system: Processing error'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="Error detected",
        action="Decline",
        action_done="False",
    )
    return transaction.__dict__


def b2binpay_more_than_deposit_diagnose(driver, this_transaction):
    more_than_deposit = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('Detected attempt of withdrawal more funds'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="b2binpay summary check",
        action="Manual",
        action_done="False",
    )
    return transaction.__dict__


def b2binpay_no_deposit_diagnose(driver, this_transaction):
    no_deposit = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('Client do not have crypto deposit'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="b2binpay summary check",
        action="Manual",
        action_done="False",
    )
    return transaction.__dict__


def b2binpay_minimum_amount_diagnose(driver, this_transaction):
    minimum_amount = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('Amount must be at least'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="b2binpay minumum amount violation",
        action="Decline",
        action_done="False",
    )
    return transaction.__dict__


def b2binpay_account_in_use_by_other_diagnose(driver, this_transaction):
    account_in_use_by_other = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.className === 'x-grid3-body').filter(el => el.textContent.includes('Bank number is used by'))[0].textContent;"
    )
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="b2binpay account in use by others",
        action="Manual",
        action_done="False",
    )
    return transaction.__dict__


def backoffice_filter_diagnose(driver, this_transaction):
    filters_and_condition = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('Reason: Client has credit') || x.textContent.includes('Transaction reaches credit boundary') || x.textContent.includes('Filter W/') || x.textContent.includes('Move to Backoffice') || x.textContent.includes('handleErrorRobot') || x.textContent.includes('Exception: Failed to load Account') || x.textContent.includes('Move to BO') || x.textContent.includes('Moved to Backoffice') || x.textContent.includes('OCR Client') || x.textContent.includes('Move to BackOffice') || x.textContent.includes('Withdrawal request was rejected') || x.textContent.includes('Move to backoffice') || x.textContent.includes('Client error')|| x.textContent.includes('Server error')).slice(-1)[0].textContent;"
    )

    funds_sent_time = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.textContent.includes('Being processed by external payment system') || el.textContent.includes('Funds sent') || el.textContent.includes('Declined')).slice(-2)[0].textContent.substring(0,19);"
    )
    processing_time_in_seconds = manual_bo_register_time_and_funds_sent_difference(
        this_transaction["register_time"], funds_sent_time
    )

    move_to_bo_time = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('Reason: Client has credit') || x.textContent.includes('Transaction reaches credit boundary') || x.textContent.includes('Filter W/') || x.textContent.includes('Move to Backoffice') || x.textContent.includes('handleErrorRobot') || x.textContent.includes('Exception: Failed to load Account') || x.textContent.includes('Move to BO') || x.textContent.includes('Moved to Backoffice') || x.textContent.includes('OCR Client') || x.textContent.includes('Move to BackOffice') || x.textContent.includes('Withdrawal request was rejected') || x.textContent.includes('Move to backoffice') || x.textContent.includes('Client error')|| x.textContent.includes('Server error')).slice(-2)[0].textContent.substring(0,19);"
    )

    waiting_bo_time_in_seconds = waiting_bo_time_difference(
        move_to_bo_time, funds_sent_time
    )

    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        register_time=this_transaction["register_time"],
        move_to_bo_time=move_to_bo_time,
        funds_sent_time=funds_sent_time,
        processing_time_in_seconds=processing_time_in_seconds,
        waiting_bo_time_in_seconds=waiting_bo_time_in_seconds,
        payment_system_status=this_transaction["payment_system_status"],
        diagnose=filters_and_condition,
        action="N/A",
        action_done="N/A",
    )
    return transaction.__dict__


def other_queue_diagnose(driver, this_transaction):
    filters_and_condition = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter( x => x.textContent.includes('oved to BO Supervisor') || x.textContent.includes('oved to Sales')).slice(-1)[0].textContent;"
    )
    funds_sent_time = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.textContent.includes('Being processed by external payment system') || el.textContent.includes('Funds sent') || el.textContent.includes('Declined')).slice(-2)[0].textContent.substring(0,19);"
    )
    processing_time_in_seconds = manual_bo_register_time_and_funds_sent_difference(
        this_transaction["register_time"], funds_sent_time
    )

    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        register_time=this_transaction["register_time"],
        move_to_bo_time="N/A",
        funds_sent_time=funds_sent_time,
        processing_time_in_seconds=processing_time_in_seconds,
        waiting_bo_time_in_seconds="N/A",
        payment_system_status=this_transaction["payment_system_status"],
        diagnose=filters_and_condition,
        action="N/A",
        action_done="N/A",
    )
    return transaction.__dict__


def robot_processing_diagnose(driver, this_transaction):
    funds_sent_time = driver.execute_script(
        "return Array.from(document.querySelectorAll('div')).filter(el => el.textContent.includes('Being processed by external payment system') || el.textContent.includes('Funds sent') || el.textContent.includes('Declined')).slice(-2)[0].textContent.substring(0,19);"
    )
    processing_time_in_seconds = manual_bo_register_time_and_funds_sent_difference(
        this_transaction["register_time"], funds_sent_time
    )

    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        register_time=this_transaction["register_time"],
        move_to_bo_time="N/A",
        processing_time_in_seconds=processing_time_in_seconds,
        waiting_bo_time_in_seconds="N/A",
        funds_sent_time=funds_sent_time,
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="robot processing transaction",
        action="N/A",
        action_done="N/A",
    )
    return transaction.__dict__


def no_comment_diagnose(driver, this_transaction):
    transaction = Transaction(
        transaction_id=this_transaction["transaction_id"],
        payment_method=this_transaction["method"],
        take_process=this_transaction["take_process"],
        give_process=this_transaction["give_process"],
        status=this_transaction["status"],
        payment_system_status=this_transaction["payment_system_status"],
        diagnose="N/A",
        action="N/A",
        action_done="N/A",
    )
    return transaction.__dict__
