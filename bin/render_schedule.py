#!/usr/bin/env python3

import sys, json, itertools, textwrap

def make_internal_header(fields):
    internal_header = """
      <tr class="active">
        <td colspan="4" class="active">{}</td>
      </tr>""".format(fields[0])
    return textwrap.dedent(internal_header)

def make_schedule_row(fields, lessons):
    date = fields[0]
    topics = ""
    readings = ""
    if fields[1] in lessons:
        lesson = lessons[fields[1]]
        topics += lesson["topic"]
        for reading in lesson["readings"]:
            readings += reading + "<br/>"
        for resource in lesson["resources"]:
            readings += resource + "<br/>"
    else:
        topics += fields[1]
    reminders = fields[2] if len(fields) == 3 else ""
    schedule_row = """
      <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
      </tr>""".format(date, topics, readings, reminders)
    return textwrap.dedent(schedule_row)


def make_schedule_table(lines, lessons):
    table = """
    <div class="table-responsive">
      <table class="table table-bordered table-hover">
        <tr class="table-header active">
          <th>Date</th>
          <th>Topics</th>
          <th>Reading and Resources</th>
          <th>Reminders</th>
        </tr>"""
    for line in lines:
        fields = [f.strip(" ") for f in line.split(";")]
        if len(fields) == 1:
            table += make_internal_header(fields)
        else:
            table += make_schedule_row(fields, lessons)

    table += """
      </table>
    </div>"""
    return textwrap.dedent(table)


if __name__=="__main__":
    schedule_spec = sys.argv[1]
    course, semester = schedule_spec.split(".")
    lessons = json.load(open("{}.json".format(course), "r"))
    fin = open(schedule_spec, "r")
    out = ""
    lines = [line.strip("\n") for line in fin.readlines()]
    header_divide = lines.index("BEGIN_SCHEDULE")
    for header in lines[:header_divide]:
        out += header + "\n"
    out += make_schedule_table(lines[header_divide + 1:], lessons)
    fout = open(semester +".html", "w")
    fout.write(out)
