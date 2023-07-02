from datetime import datetime, timedelta


def comment_time_compare(last_update_time):
    now = datetime.now().replace(microsecond=0)
    update = datetime.strptime(last_update_time, "%d.%m.%Y %H:%M") + timedelta(hours=2)
    if now - update <= timedelta(hours=24):
        return True
    else:
        return False


def register_time_sla_violation(register_time):
    now = datetime.now().replace(microsecond=0)
    regist = datetime.strptime(register_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=2)
    if now - regist <= timedelta(hours=24):
        return False
    else:
        return True


def violation_delta(register_time):
    now = datetime.now().replace(microsecond=0)
    regist = datetime.strptime(register_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=2)
    time_to_violation = timedelta(hours=24) - (now - regist)
    return time_to_violation


def reminder_time(last_doc_request_time):
    now = datetime.now().replace(microsecond=0)
    last_doc_request_uae = datetime.strptime(
        last_doc_request_time, "%d.%m.%Y %H:%M"
    ) + timedelta(hours=2)
    time_to_remind = timedelta(hours=12) - (now - last_doc_request_uae)
    if time_to_remind > timedelta(hours=0):
        return time_to_remind
    else:
        return False

def ps356_register_time_and_funds_credited_difference(timestamp1_str, timestamp2_str):
    timestamp1 = datetime.strptime(timestamp1_str, '%Y-%m-%d %H:%M:%S')
    timestamp2 = datetime.strptime(timestamp2_str, '%d.%m.%Y %H:%M:%S')
    seconds_difference = (timestamp2 - timestamp1).total_seconds()
    return seconds_difference

def manual_bo_register_time_and_funds_sent_difference(timestamp1_str, timestamp2_str):
    timestamp1 = datetime.strptime(timestamp1_str, '%Y-%m-%d %H:%M:%S')
    timestamp2 = datetime.strptime(timestamp2_str, '%d.%m.%Y %H:%M:%S')
    seconds_difference = (timestamp2 - timestamp1).total_seconds()
    return seconds_difference

def waiting_bo_time_difference(timestamp1_str, timestamp2_str):
    timestamp1 = datetime.strptime(timestamp1_str, '%d.%m.%Y %H:%M:%S')
    timestamp2 = datetime.strptime(timestamp2_str, '%d.%m.%Y %H:%M:%S')
    seconds_difference = (timestamp2 - timestamp1).total_seconds()
    return seconds_difference