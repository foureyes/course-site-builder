#!/usr/bin/env python3
"""Commandline utility for building and deploying course sites hosted on github.
"""
import argparse
import subprocess
import sys
import codecs
import os
import traceback
import smtplib
from email.message import EmailMessage

##
# The following can be defined via commandline arguments, but
# default values can be placed below
##

# directory that contains clones of course sites
DEFAULT_STAGING_PATH = ''

# absolute path to directory that contains course all course sites w/ out semeseter and #
DEFAULT_COURSES_BASE_PATH = '' 

# smpt server for sending error emails
DEFAULT_SERVER = ''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_name")
    parser.add_argument("--staging", default=DEFAULT_STAGING_PATH)
    parser.add_argument("--target", default=DEFAULT_COURSES_BASE_PATH)
    parser.add_argument("--erroremail", default='')
    parser.add_argument("--sender", default='')
    parser.add_argument("--server", default=DEFAULT_SERVER)
    parser.add_argument("--log", default='')
    args = parser.parse_args()

    try:
        result = build(args.repo_name, args.staging, args.target)
        report = ''
        for step, output in result.items():
            report += step.upper() + '\n===\n'
            report += str(output) + '\n\n'

        print(report)

        if args.log:
            with open(args.log, 'w') as f:
                f.write(report)

    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        if args.erroremail:
            subject =  'Error building {}'.format(args.repo_name)
            send_email(args.sender, args.erroremail, subject, tb, args.server)
            print('Error email sent!')
        

class CourseSitePathError(Exception):
    pass

def build(repo_name, staging_path, courses_base_path):

    available_repos = os.listdir(staging_path)

    if repo_name not in available_repos:
        raise CourseSitePathError('{} not in {}'.format(repo_name, available_repos))

    course_site_path = extract_course_site_path(repo_name, courses_base_path)
    repo_path = os.path.join(staging_path, repo_name)

    pull_output = pull(repo_path)
    jekyll_output = jekyll(repo_path)
    sync_output = sync(repo_path, course_site_path)

    return {'pull': pull_output, 'jekyll': jekyll_output, 'sync': sync_output}

def sync(repo_path, course_site_path):

    # force source to include trailing slash so that rsync does not create 
    # source directory in destination
    source = os.path.join(repo_path, '_site')
    output = subprocess.run(['rsync', '-avzh', '--perms', '--chmod=o+rx', source, course_site_path], cwd=source, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return output

def extract_course_site_path(repo_name, courses_base_path):
    """parses out path to course site based on repo name
    
    if there is more than one section number, only use last
    (assume other sections will just redirect)

    transforms repo_name to course site path...
 
    1. repo name: 'csci-ua.0480-fall2018-001-003'
    2. course site path: 'fall18/CSCI-UA.0480-003/'
    """

    SECTION_INDEX = -1
    SEMESTER_INDEX = 2
    COURSE_INDEX = 1
    DEPT_INDEX = 0

    repo_name_parts = repo_name.split('-')
    section = repo_name_parts[SECTION_INDEX]
    semester = repo_name_parts[SEMESTER_INDEX].replace('20', '', 1)
    course = '{}-{}'.format(repo_name_parts[DEPT_INDEX], repo_name_parts[COURSE_INDEX]).upper()
    format_str = '{}.{}' if semester == 'spring20' and course == '0479' else '{}-{}'
    path = os.path.join(courses_base_path, semester, format_str.format(course, section))
    
    return path

def pull(repo_path):
    """run git pull from repo_path
    """
    output = subprocess.run(['git', 'pull'], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    return output

def jekyll(repo_path):
    """run jekyll from repo_path
    """
    cmd = '/usr/local/pkg/ruby/2.5/bin/jekyll'
    output = subprocess.run([cmd, 'build', '--incremental'], cwd=repo_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    return output



def send_email(sender, recipient, subject, body, server):

    msg = EmailMessage()
    msg.set_content(body)

    msg['Subject'] = subject 
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP(server)
    s.send_message(msg)
    s.quit()

if __name__ == '__main__':
    main()
