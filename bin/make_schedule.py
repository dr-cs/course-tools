#!/usr/bin/env python3

import argparse
import json
import sys
import datetime as dt

def class_dates(first, last, class_days):
    """Generate dates from first to last whose weekdays are in class_days

    >>> import datetime
    >>> begin = datetime.date(2016, 8, 22)
    >>> end = datetime.date(2016, 8, 25)
    >>> list(class_dates(begin, end, "TR"))
    [datetime.date(2016, 8, 23), datetime.date(2016, 8, 25)]
    """
    day = first
    # e.g., "MWF" => [0, 2, 4]
    class_day_ints = [i for i, letter in enumerate("MTWRFSU")
                           if letter in class_days]
    while day <= last:
        if day.weekday() in class_day_ints:
            yield day
        day += dt.timedelta(days=1)

def make_argparser():
    parser = argparse.ArgumentParser(description='Generate class schedule.')
    parser.add_argument("-f", "--first", dest="first", required=True,
                        help="The first class date, in ISO format")
    parser.add_argument("-l", "--last", dest="last", required=True,
                        help="The last class date, in ISO format")
    parser.add_argument("-d", "--days", dest="days", required=True,
                        help="Class days, e.g., TR for Tuesdays and Thursdays")
    parser.add_argument("-b", "--breaks", dest="breaks", required=False,
                        help="File containing JSON dict of breaks/holidays.")
    parser.add_argument("-c", "--course", dest="course", required=False,
                        help="JSON course. If absent, generate blank schedule.")
    parser.add_argument("-o", "--output", dest="output", required=False,
                        help="File to write schedule to.")
    return parser


def make_order2lesson(course):
    if not course:
        return None
    # make a dict mapping lesson order to lesson key in course
    order2lesson = {}
    for lesson in course.keys():
        if "order" in course[lesson]:
            # lesson is a list of ints - map each one to lesson
            # represents lessons that span multiple class days
            for i in course[lesson]["order"]:
                order2lesson[i] = lesson
    return order2lesson

def main(argv):
    parser = make_argparser()
    args = parser.parse_args(argv[1:])
    first = dt.datetime.strptime(args.first, "%Y-%m-%d").date()
    last = dt.datetime.strptime(args.last, "%Y-%m-%d").date()
    breaks = json.load(open(args.breaks, 'r')) if args.breaks else None
    course = json.load(open(args.course, 'r')) if args.course else None
    order2lesson = make_order2lesson(course)
    fout = open(args.output, 'w') if args.output else sys.stdout
    lesson_number = 1
    last_class = first
    print("Week 1", file=fout)
    week = 2
    for class_date in class_dates(first, last, args.days):
        if class_date.weekday() < last_class.weekday():
            print("Week {}".format(week), file=fout)
            week += 1
        last_class = class_date
        schedule_line = [class_date.isoformat()]
        if breaks and class_date.isoformat() in breaks:
            schedule_line.append(
                "{} - No Class".format(breaks[class_date.isoformat()]))
        elif course and lesson_number in order2lesson:
            schedule_line.append(order2lesson[lesson_number])
            lesson_number += 1
        print(";".join(schedule_line), file=fout)



if __name__=="__main__":
    main(sys.argv)
