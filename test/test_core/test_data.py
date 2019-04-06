#
# AtraxiFlow - Flexible python workflow tool
#
# Copyright (C) 2019  Sean Mertiens
# For more information on licensing see LICENSE file
#

from datetime import datetime, timedelta

from atraxiflow.core.data import StringValueProcessor, DatetimeProcessor
from atraxiflow.core.stream import Stream
from atraxiflow.nodes.text import TextResource


def get_stream_for_test():
    st = Stream()
    st.add_resource(TextResource("text1", {"text": "one"}))
    st.add_resource(TextResource("text2", {"text": "two"}))
    return st


def test_find_vars_and_replace_simple():
    p = StringValueProcessor(Stream())
    p.add_variable("demo", "omed")
    p.add_variable("one", "eno")
    p.add_variable("two", "owt")
    out = p.parse("Hello World {demo} and  another {one}, {two}.")

    assert "Hello World omed and  another eno, owt." == out


def test_find_vars_and_replace_resource():
    st = get_stream_for_test()
    p = StringValueProcessor(st)
    p.add_variable("demo", "omed")

    out = p.parse("Hello World {demo} and  another {Text:text1}, {Text:text2}.")
    assert "Hello World omed and  another one, two." == out


def test_datetime_processor_named():
    dp = DatetimeProcessor()

    assert dp.process_string('today').replace(microsecond=0) == datetime.now().replace(microsecond=0)
    assert dp.process_string('yesterday').replace(microsecond=0) == datetime.now().replace(microsecond=0) - timedelta(
        days=1)
    assert dp.process_string('tomorrow').replace(microsecond=0) == datetime.now().replace(microsecond=0) + timedelta(
        days=1)


def test_datetime_processor_dateformats():
    dp = DatetimeProcessor()

    test_date_1 = datetime(year=2019, month=4, day=5)

    assert dp.process_string('05.04.2019') == test_date_1
    assert dp.process_string('05.04.19') == test_date_1
    assert dp.process_string('04/05/2019') == test_date_1
    assert dp.process_string('04/05/19') == test_date_1


def test_datetime_processor_datetimeformats():
    dp = DatetimeProcessor()

    test_date_1 = datetime(year=2019, month=4, day=5, hour=10, minute=34, second=12)

    assert dp.process_string('05.04.2019 10:34:12') == test_date_1
    assert dp.process_string('05.04.19 10:34:12') == test_date_1
    assert dp.process_string('05.04.2019 10:34') == test_date_1.replace(second=0)
    assert dp.process_string('05.04.2019') == test_date_1.replace(second=0, minute=0, hour=0)

    assert dp.process_string('04/05/2019 10:34:12') == test_date_1
    assert dp.process_string('04/05/19 10:34:12') == test_date_1
    assert dp.process_string('04/05/2019 10:34') == test_date_1.replace(second=0)
    assert dp.process_string('04/05/2019') == test_date_1.replace(second=0, minute=0, hour=0)


def test_datetime_processor_return_now_on_error():
    dp = DatetimeProcessor()

    assert dp.process_string('something').replace(microsecond=0) == datetime.now().replace(microsecond=0)
