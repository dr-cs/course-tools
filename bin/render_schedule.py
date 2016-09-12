#!/usr/bin/env python3

import argparse
import sys
import json
import jinja2
import pprint as pp
import markdown

def make_argparser():
    parser = argparse.ArgumentParser(description='Generate class schedule.')
    parser.add_argument("-s", "--schedule", dest="schedule", required=True,
                        help="Schedule file, as produced by make_schedule.py")
    parser.add_argument("-c", "--course", dest="course", required=True,
                        help="JSON file containing course dict.")
    parser.add_argument("-t", "--template", dest="template_file", required=True,
                        help="Template file used for rendering schedule.")
    parser.add_argument("-o", "--output", dest="output", required=False,
                        help="Name of file to write rendered schedule to.")
    return parser


def main(argv):
    parser = make_argparser()
    args = parser.parse_args(argv[1:])
    schedule_file = open(args.schedule, 'r')
    course = json.load(open(args.course, 'r'))
    rows = []
    for line in schedule_file:
        fields = [field.strip() for field in line.split(";")]
        if len(fields) == 1:
            rows.append({"internal_header": fields[0]})
        elif fields[1] in course:
            rows.append({"date": fields[0],
                         "topic": course[fields[1]]["topic"],
                         "materials": course[fields[1]]["materials"],
                         "reminders": (fields[2].split(",") if len(fields) > 2
                                       else [""])
                         })
        else:
            rows.append({"date": fields[0],
                         "topic": fields[1] if len(fields) > 1 else "",
                         "materials": (fields[2].split(",") if len(fields) > 2
                                       else [""]),
                         "reminders": (fields[3].split(",") if len(fields) > 3
                                       else [""])
                         })
    env = jinja2.Environment()
    env.filters['markdown'] = markdown.markdown
    template = env.from_string(open(args.template_file, 'r').read())
    fout = open(args.output, 'w') if args.output else sys.stdout
    print(template.render(table=rows), file=fout)

if __name__=="__main__":
    main(sys.argv)
