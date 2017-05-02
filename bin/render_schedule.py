#!/usr/bin/env python3

import argparse
import sys
import json
import jinja2
from pprint import pprint
import markdown
from functools import reduce

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

def topics(topics, course, key="topic"):
    items = [item.strip() for item in topics.split(",")]
    return [course[item][key] if (item in course) else item
            for item in items]

def materials(topics, materials, course):
    topic_items = [item.strip() for item in topics.split(",")]
    materials_items = [item.strip() for item in materials.split(",")]
    lecture_materials = reduce(lambda a, b: a + b,
                               [course[item]["materials"]
                                for item in topic_items if item in course],
                               [])
    return (lecture_materials + [item for item in materials_items])

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
        else:
            rows.append({"date": fields[0],
                         "topics": (topics(fields[1], course)
                                    if len(fields) > 1
                                    else [""]),
                         "materials": (materials(fields[1],
                                                 fields[2] if len(fields) > 2 else "",
                                                 course)
                                       ),
                         "reminders": (fields[3].split(",")
                                       if len(fields) > 3
                                       else [""])
                         })
    env = jinja2.Environment()
    env.filters['markdown'] = markdown.markdown
    template = env.from_string(open(args.template_file, 'r').read())
    fout = open(args.output, 'w') if args.output else sys.stdout
    print(template.render(table=rows), file=fout)

if __name__=="__main__":
    main(sys.argv)
