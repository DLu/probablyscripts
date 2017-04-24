#!/usr/bin/python

from urlgrabber import urlread
from xml.dom import minidom

def text(n, x):
    return n.getElementsByTagName(x)[0].firstChild.nodeValue.strip()

URL = "https://acadinfo.wustl.edu/sis_ws_courses/SIScourses.asmx/GetCoursesByCourseNumbyASemester?ApplicationToken=c09fbe82-7375-4df6-9659-b4f2bf21e4b9&ApplicationPwd=876KKmp*cR478Q&SortSemester=201502&DeptCd=E81&SchoolCd=E&CrsNum="

for course in ['365S', '550S']:
    xml = urlread(URL + course)

    xmldoc = minidom.parseString(xml)

    title = text(xmldoc, 'CourseTitle')
    print title

    for tag in xmldoc.getElementsByTagName('CourseSection'):
        section = text(tag, 'Section')
        enrolled = text(tag, 'EnrollCnt')
        limit = text(tag, 'EnrollLimit')
        wait = text(tag, 'WaitCnt')
        print '\t%3s %03d/%03d    Waiting: %d'%(section, int(enrolled), int(limit), int(wait))

