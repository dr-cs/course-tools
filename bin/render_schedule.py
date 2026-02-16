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
    parser.add_argument("-i", "--semester-info", dest="semester_info", required=True,
                        help="JSON file containing semester information.")
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

def main(args):
    schedule_file = open(args.schedule, 'r')
    course = json.load(open(args.course, 'r'))
    semester_info = json.load(open(args.semester_info, 'r'))
    all_lessons = course["lessons"] \
        if isinstance(course["lessons"], list) \
        else json.load(open(course["lessons"], "r"))
    lessons = {lesson["topic"]: lesson for lesson in all_lessons
               if "topic" in lesson}
    rows = []
    frontmatter = [
        ["Meeting times", semester_info["meeting_times"]],
        ["Room", semester_info["room"]]
    ]
    for line in schedule_file:
        fields = [field.strip() for field in line.split(";")]
        if len(fields) == 1:
            rows.append({"internal_header": fields[0]})
        elif fields[1].split(",")[0] in lessons:
            # We have a (list of) lesson(s)
            slides = [lessons[lesson]["slides"]
                      for lesson in fields[1].split(",")]
            readings = [lessons[lesson]["reading"] +
                        [f"Video: {v}" for v in lessons[lesson]["videos"]]
                        for lesson in fields[1].split(",")]
            readings = reduce(lambda a, b: a + b, readings)
            exercises = [lessons[lesson]["exercises"] for lesson in fields[1].split(",")]
            exercises = reduce(lambda a, b: a + b, exercises)
            rows.append({"date": fields[0],
                         "slides": slides,
                         "reading": readings if readings else [""],
                         "exercises": exercises if exercises else [""],
                         "assignments": fields[2].split(","),
                         "reminders": fields[3].split(",")
                         })
        else:
            rows.append({"date": fields[0], # date
                         "slides": [fields[1]], # empty, or holiday
                         "reading": [""],
                         "exercises": [""],
                         "assignments": [""],
                         "reminders": fields[3].split(",")
                         })
    env = jinja2.Environment()
    env.filters['markdown'] = markdown.markdown
    template = env.from_string(open(args.template_file, 'r').read())
    fout = open(args.output, 'w') if args.output else sys.stdout
    print(template.render(frontmatter=frontmatter,
                          required_materials=course["required_materials"],
                          recommended_materials=course["recommended_materials"],
                          table=rows),
          file=fout)

if __name__=="__main__":
    parser = make_argparser()
    args = parser.parse_args(sys.argv[1:])
    main(args)
