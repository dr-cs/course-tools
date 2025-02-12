#!/usr/bin/env python3

import argparse
import sys
import json
import jinja2
from pprint import pprint
import markdown
import re

def make_argparser():
    parser = argparse.ArgumentParser(description='Generate class schedule.')
    parser.add_argument("-c", "--course", dest="course", required=True,
                        help="JSON file containing course dict.")
    parser.add_argument("-i", "--semester_info", dest="semester_info", required=True,
                        help="JSON file containing semester information.")
    parser.add_argument("-s", "--schedule", dest="schedule", required=True,
                        help="Schedule file produced by make_schedule.py")
    parser.add_argument("-t", "--template", dest="template_file", required=True,
                        help="Template file used for rendering syllabus.")
    parser.add_argument("-o", "--output", dest="output", required=False,
                        help="Name of file to write rendered syllabus to.")
    return parser

def mk_schedule(schedule_file: str, course: dict) -> list[list[str]]:
    lessons = {lesson["topic"]: lesson for lesson in course["lessons"]
               if "topic" in lesson}
    schedule = [
        ["Week", "Content Covered", "Assignments", "Exams"]
    ]
    dates = ""
    topics = ""
    assignments = ""
    exams = ""
    prev_week = ["", "", "", ""]
    with open(schedule_file, 'rt') as fin:
        for line in fin:
            fields = line.split(";")
            if len(fields) == 1 and fields[0].startswith("Week"):
                if prev_week[0]:
                    # Strip trailing commas
                    prev_week = [s[:-1] if (s and s[-1] == ",") else s for s in prev_week]
                    schedule.append(prev_week)
                prev_week = [f"{fields[0][:-1]}: ","","",""]
            elif len(fields) == 4:
                prev_week[0] += fields[0][5:] + ","
                if fields[1] in lessons:
                    content: str = markdown.markdown(lessons[fields[1]]["slides"])
                    content = re.sub('<[^<]+?>', '', content)
                    if "exam" in content.lower() and "review" not in content.lower():
                        prev_week[3] = content
                    elif content not in prev_week[1]:
                        prev_week[1] += content +","
                elif fields[1] not in prev_week[1]:
                    prev_week[1] += fields[1] + ","
                if fields[2]:
                    assignments: str = markdown.markdown(fields[2])
                    assignments = re.sub('<[^<]+?>', '', assignments)
                    prev_week[2] += assignments + ","
        prev_week = [s[:-1] if (s and s[-1] == ",") else s for s in prev_week]
        schedule.append(prev_week)
    return schedule

def main(argv):
    parser = make_argparser()
    args = parser.parse_args(argv[1:])
    course = json.load(open(args.course, 'r'))
    semester_info = json.load(open(args.semester_info, 'r'))
    schedule = mk_schedule(args.schedule, course)
    env = jinja2.Environment()
    env.filters['markdown'] = markdown.markdown
    template = env.from_string(open(args.template_file, 'r').read())
    fout = open(args.output, 'w') if args.output else sys.stdout
    print(template.render(course=course,
                          semester_info=semester_info,
                          schedule=schedule),
          file=fout)

if __name__=="__main__":
    main(sys.argv)
