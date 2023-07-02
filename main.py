import concurrent.futures
import time

from processing import Status1Processing, Status2Processing
from reports import final_report
import time


NOW = int(time.time())


def start_processing_status1():
    driver1 = Status1Processing(window_size="normal", processing=False, time=NOW)
    driver1.start_processing(
        queue="Current Transactions",
        transaction_type="Withdrawal",
        payment_system="api_methods",
        table_name=f"api_methods_{NOW}",
        db="statement.sqlite",
    )


def start_processing_status2():
    driver2 = Status2Processing(window_size="normal", processing=False, time=NOW)
    driver2.start_processing(
        queue="Current Transactions",
        transaction_type="Withdrawal",
        payment_system="api_methods",
        table_name=f"api_methods_{NOW}",
        db="statement.sqlite",
    )


def main():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(start_processing_status1)
        time.sleep(3)
        executor.submit(start_processing_status2)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(final_report, time=NOW)


if __name__ == "__main__":
    main()
