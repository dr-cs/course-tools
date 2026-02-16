#!/usr/bin/env python3

import argparse
import collections
import json
import sys
import datetime as dt

def gen_class_dates(first, last, class_days):
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

    parser.add_argument("-i", "--semester-info", dest="semester_info",
                        required=True,
                        help=("File containing JSON dict first day, last day, "
                             "class days, meeting days/times, breaks/holidays, "
                              "and reminders."))
    parser.add_argument("-c", "--course", dest="course", required=False,
                        help="JSON course. If absent, generate blank schedule.")
    parser.add_argument("-o", "--output", dest="output", required=False,
                        help="File to write schedule to.")
    return parser

def timely_reminders(from_date, to_date, reminders):
    if not reminders: return ""
    d = from_date
    rems = [f"{rem} ({d.isoformat()})" for rem in reminders[d.isoformat()].split(",")] \
           if d.isoformat() in reminders else []
    d += dt.timedelta(days=1)
    while d < to_date:
        if d.isoformat() in reminders:
            for rem in reminders[d.isoformat()].split(","):
                rems.append(f"{rem} ({d.isoformat()})")
        d += dt.timedelta(days=1)
    return ",".join(rems) if rems else ""

def next_lesson(lesson_iter):
    try:
        return next(lesson_iter)
    except StopIteration:
        return {}

def next_included_lesson(lesson, lesson_iter):
    while ("include_semester" in lesson) and lesson["include_semester"] is False:
        lesson = next(lesson_iter)
    return lesson

def is_included(lesson):
    return ("include_semester" not in lesson) or \
        (lesson["include_semester"] is True)

def main(argv):
    parser = make_argparser()
    args = parser.parse_args(argv[1:])
    semester_info = json.load(open(args.semester_info, "r")) if args.course else None
    course = json.load(open(args.course, "r")) if args.course else None
    lessons = course["lessons"] \
        if isinstance(course["lessons"], list) \
        else json.load(open(course["lessons"], "r"))
    lessons = [lesson for lesson in lessons if is_included(lesson)]
    num_topics = sum([1 for lesson in lessons if "topic" in lesson])
    fout = open(args.output, 'w') if args.output else sys.stdout
    first = dt.datetime.strptime(semester_info["first_day"], "%Y-%m-%d").date()
    last = dt.datetime.strptime(semester_info["last_day"], "%Y-%m-%d").date()
    breaks = semester_info["breaks"]
    reminders = semester_info["reminders"]
    # print(f"Meeting times;{semester_info['meeting_times']}", file=fout)
    # print(f"Room;{semester_info['room']}", file=fout)
    prev_class = first
    week = 1
    lesson_iter = iter(lessons)
    included_topics = 0
    class_dates = list(gen_class_dates(first, last, semester_info["days"]))
    is_first_day = True
    lesson = next_lesson(lesson_iter)
    assignments = ",".join(lesson["assignments"]) if "assignments" in lesson else ""
    for i, class_date in enumerate(class_dates):
        # Non-topics that "consume" the lesson.
        if "part" in lesson:
            print(lesson["part"], file=fout)
            lesson = next_lesson(lesson_iter)

        if is_first_day or (class_date.weekday() < prev_class.weekday()):
            print(f"Week {week}", file=fout)
            week += 1
            is_first_day = False

        if breaks and class_date.isoformat() in breaks:
            topic =  f"{breaks[class_date.isoformat()]} - No Class"
            assignments = ""
        elif ("topic" in lesson):
            topic = lesson["topic"]
            included_topics += 1
            assignments = ",".join(lesson["assignments"]) if "assignments" in lesson else ""
            lesson = next_lesson(lesson_iter)
        else:
            topic, assignments = "", ""
        class_date_iso = class_date.isoformat()
        prev_class = class_date
        next_class = class_dates[i + 1] if i + 1 < len(class_dates) else class_date
        rems = timely_reminders(class_date, next_class, reminders)
        line = f"{class_date_iso};{topic};{assignments};{rems}"
        print(line, file=fout)

    for date, time in semester_info["final_exam"].items():
        line = f"{date};Final Exam;;{time}"
        print(line, file=fout)
    print(f"{included_topics=} out of {num_topics=} from {args.course=}.")



if __name__=="__main__":
    main(sys.argv)
