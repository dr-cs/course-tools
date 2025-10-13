#!/usr/bin/env python3

import argparse
import os
import render_schedule
import render_syllabus
import sys


def make_argparser():
    parser = argparse.ArgumentParser(description='Generate class schedule.')
    parser.add_argument("-c", "--course", dest="course", required=True,
                        help="JSON file containing course dict.")
    parser.add_argument("-i", "--semester_info", dest="semester_info", required=True,
                        help="JSON file containing semester information.")
    parser.add_argument("-s", "--schedule", dest="schedule", required=True,
                        help="Schedule file produced by make_schedule.py")
    parser.add_argument("-t", "--template", dest="template_dir", required=True,
                        help=("Directory containing" +
                              "syllabus-template.html.jinja2 and " +
                              "schedule-template.html.jinja2."))
    parser.add_argument("-p", "--prefix", dest="prefix", required=False,
                        help=("File prefix, e.g., 'fall2025' to produce " +
                              "'fall2025syllabus.html' and " +
                              "'fall2025schedule.html'"))
    return parser


def main(args):
    args.template_file = os.path.join(args.template_dir,
                                      "syllabus-template.html.jinja2")
    args.output = f"{args.prefix}syllabus.html"
    print(f"Writing syllabus to {args.output}")
    render_syllabus.main(args)

    args.template_file = os.path.join(args.template_dir,
                                      "schedule-template.html.jinja2")
    args.output = f"{args.prefix}schedule.html"
    print(f"Writing schedule to {args.output}")
    render_schedule.main(args)


if __name__=="__main__":
    parser = make_argparser()
    args = parser.parse_args(sys.argv[1:])
    main(args)
