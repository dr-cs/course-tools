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
    parser.add_argument("-c", "--course", dest="course", required=True,
                        help="JSON file containing course dict.")
    parser.add_argument("-l", "--lessons", dest="lessons", required=True,
                        help="JSON file containing lessons list.")
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
    course = json.load(open(args.course, 'r'))
    lessons = json.load(open(args.lessons, 'r'))

    rows = []
    lesson_number = 1
    for lesson in lessons:
        if "part" in lesson:
            rows.append({"internal_header": lesson["part"]})
        elif (("review" not in lesson["topic"].lower()) and
              ("exam" not in lesson["topic"].lower())):
            readings = lesson["reading"] + [f"Video: {v}" for v in lesson["videos"]]
            rows.append({"date": lesson_number,
                         "slides": lesson["slides"],
                         "reading": readings if readings else [""],
                         "exercises": (lesson["exercises"]
                                       if lesson["exercises"] else [""])
                         })
            lesson_number += 1
    env = jinja2.Environment()
    env.filters['markdown'] = markdown.markdown
    template = env.from_string(open(args.template_file, 'r').read())
    fout = open(args.output, 'w') if args.output else sys.stdout
    print(template.render(required_materials=course["required_materials"],
                          recommended_materials=course["recommended_materials"],
                          table=rows),
          file=fout)

if __name__=="__main__":
    parser = make_argparser()
    args = parser.parse_args(sys.argv[1:])
    main(args)
