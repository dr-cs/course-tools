#!/usr/bin/env python3

import sys
import datetime as dt

def class_dates(first, last, days):
    one_day = dt.timedelta(1)
    day = first
    class_days = [i for i, letter in enumerate("MTWRFSU") if letter in days]
    while day <= last:
        if day.weekday() in class_days:
            yield day
        day += one_day

def main(args):
    first = dt.datetime.strptime(args[1], "%Y-%m-%d").date()
    last = dt.datetime.strptime(args[2], "%Y-%m-%d").date()
    for day in class_dates(first, last, args[3]):
        print(day.isoformat())


if __name__=="__main__":
    main(sys.argv)
