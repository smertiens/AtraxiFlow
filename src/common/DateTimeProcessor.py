from datetime import datetime, timedelta

def processString(str):
    if "today" == str:
        return datetime.now()
    elif "yesterday" == str:
        return datetime.now() - timedelta(days=1)
    else:
        return datetime.strptime(str)
