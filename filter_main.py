import concurrent.futures
import time

from processing import FilterStatus1Processing, FilterStatus2Processing
from reports import final_report


def start_processing_status1():
    driver1 = FilterStatus1Processing(window_size="normal", processing=False)
    withdrawal_report = driver1.start_processing()
    return withdrawal_report


def start_processing_status2():
    driver2 = FilterStatus2Processing(window_size="normal", processing=False)
    withdrawal_report = driver2.start_processing()
    return withdrawal_report


def main():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        driver1 = executor.submit(start_processing_status1)
        # time.sleep(3)
        driver2 = executor.submit(start_processing_status2)
        status1_report = driver1.result()
        status2_report = driver2.result()
        final_report(status1_report, status2_report)


if __name__ == "__main__":
    main()
