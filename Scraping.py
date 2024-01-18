# These are the imports to be made
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from datetime import datetime

url = 'https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept=MATH&course=100&campuscd=UBCO'

labs = False
specific = False
sections = ['102']


def __init__(url_inp, labs_inp, specific_inp):
    global url
    url = url_inp
    global labs
    labs = labs_inp
    global specific
    specific = specific_inp


def specifics(inputs):
    if specific:
        global sections
        sections.clear()
        for x in inputs:
            sections.append(x)


status = []
course = []
links = []


def __main__():
    driver = webdriver.Chrome()
    driver.implicitly_wait(0.5)
    driver.get(url)

    # section1 = lec
    # section2 = labs || discussions
    # a waitList can be either
    # in the event there are no labs|discussions, section2 is another lec
    if labs:
        l = driver.find_elements(By.CLASS_NAME, 'section1')
    else:
        l1 = driver.find_elements(By.CLASS_NAME, 'section1')
        l2 = driver.find_elements(By.CLASS_NAME, 'section2')
        l = [l1[0]]
        i = 1
        no_last = False
        if len(l1) == len(l2):
            no_last = True
        for item in l2:
            l.append(item)
            if not(i == (len(l2) - 1) and no_last):
                l.append(l1[i])
            i = i + 1

    found = False

    if specific:
        for item in l:
            data = item.get_attribute('innerHTML')
            for section in sections:
                if data.find(section):
                    found = True
                    break
            if not found:
                l.remove(item)
            found = False

    for item in l:
        data = item.get_attribute('innerHTML')
        split = data.split('</td>')
        if ' ' in split[0].split('>')[1]:
            status.append('Space')
        else:
            status.append(split[0].split('>')[1])
        # print(status[-1])
        course.append(split[1].split('">')[1].split('</')[0])
        # print(course[-1])
        temp = 'https://courses.students.ubc.ca' + split[1].split('">')[0].split('"')[1]
        link = ''
        for part in temp.split('amp;'):
            link = link + part
        links.append(link)
        # print(link)


def remove_not_filled():
    if not empty():
        # for loops use lists so the direct manupliation of vars not good, while is better. Change
        # range(0,5) returns a list of [0,1,2,3,4,5] so the i manuplation changes the int at i index, we never
        # check that int again making that code useless.
        i = 0
        while True:
            if i >= len(status):
                break
            if not ('Space' == status[i]):
                status.remove(status[i])
                course.remove(course[i])
                links.remove(links[i])
                i -= 1
            i += 1


def empty():
    if len(status) == 0:
        return True
    else:
        return False


def return_status():
    return status


def return_courses():
    return course


def return_links():
    return links
