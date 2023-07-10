from single_method_analyze import (
    PS356DepositBinChecker,
    ManulBoAnalyzier,
)
from typeguard import typechecked


@typechecked
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


@typechecked
def manual_bo():
    manul_bo = ManulBoAnalyzier(window_size="normal")
    manul_bo.check(
        queue="Archive",
        transaction_type="Withdrawal",
        time_from="2023-06-27",
        time_to="2023-06-30",
        payment_system="api_methods_withdrawal_June_test",
        transaction_status_code="4",
        db="singlemethod.sqlite",
    )

    
manual_bo()