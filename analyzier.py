from single_method_analyze import (
    PS356DepositBinChecker,
    ManulBoAnalyzier,
    ManulMethods,
    Filter,
)



def bin_checker():
    bin_checker = PS356DepositBinChecker(window_size="normal", page=1)
    bin_checker.check(
        ps_id="356",
        queue="Archive",
        transaction_type="Deposit",
        time_from="2023-03-15",
        time_to="2023-03-15",
        transaction_status_code="3",
        payment_system="Praxis_Card",
        db="singlemethod.sqlite",
    )

def manual_bo():
    manul_bo =  ManulMethods(window_size="normal")
    manul_bo.check(
        queue="Archive",
        transaction_type="Withdrawal",
        time_from="2023-07-02",
        time_to="2023-07-31",
        payment_system="api_methods_withdrawal_July_manual",
        # transaction_status_code="3",
        db="singlemethod.sqlite",
    )


manual_bo()

def get_fxtm_filter():
    filter = Filter(window_size="normal")
    filter.check(
        payment_system="filters",
        db="singlemethod.sqlite")


def get_asv_filter():
    filter = Filter(window_size="normal")
    filter.check(
        payment_system="filters",
        db="singlemethod.sqlite")