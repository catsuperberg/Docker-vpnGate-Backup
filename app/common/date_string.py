import datetime

def get_current_timestemp():
    now = datetime.datetime.now()
    return now.strftime("%Y.%m.%d %H-%M")