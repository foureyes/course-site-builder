#!/usr/bin/env python3
"""webhook for building course sites after commits to github repository
"""
import cgi
import cgitb
import json
import subprocess
import codecs
import traceback
import os


def main():
    # enable stacktrace for cgi
    cgitb.enable()

    # grab post variables
    POST = cgi.FieldStorage()

    # one of the post variables should be payload, meta info about the
    # event in json format
    payload = POST['payload']
    
    # uncomment this to debug!
    #payload = get_test_json()

    print('Content-Type: application/json', end='\r\n\r\n')
    print(json.dumps({'received': payload.value}))

    if payload:
        try:
            repo_name = extract_repo_name(payload.value)
        except Exception as e:
            handle_error('could not extract name from json: {}'.format(payload.value), e)
        

        ##
        # TODO: complete the configuration options below
        ##
        cmd = '' # absolute path to location of build_course_site.py
        erroremail = '--erroremail=' # append email address of where error messages should be sent
        sender = '--sender=' # append eemail address of sender
        log = '--log=' # absolute path to location of build logs

        subprocess.Popen([cmd, repo_name, erroremail, sender, log], stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        # TODO: find better way to terminate script without waiting for
        # child proc
        os._exit(0)
    else:
        handle_error('no payload, POST was: {}'.format(POST))


def extract_repo_name(payload_json):
    """parse out repository name from json POSTed to this webhook
    """
    try:
        payload = json.loads(payload_json) 
        repo_info = payload.get('repository')
        repo_name = repo_info.get('name')
    except Exception as e:
        raise e

    return repo_name

def handle_error(msg, e=None):
    print('Content-Type: text/html', end='')
    print('<pre>\nERROR\n=====\n\n{}</pre>'.format(msg))
    print('EXCEPTION was: ', e, e.__traceback__)
    print(traceback.format_exc())
    os._exit(0)


def get_test_json():
   return """
{
  "repository": {
    "id": 145344764,
    "name": "csci-ua.0480-fall2018-001-003",
    "full_name": "foureyes/csci-ua.0480-fall2018-001-003",
    "owner": {
      "name": "foureyes",
      "url": "https://api.github.com/users/foureyes"
    },
    "private": false,
    "html_url": "https://github.com/foureyes/csci-ua.0480-fall2018-001-003"
  },
  "pusher": {
    "name": "foureyes",
    "email": "joeversoza@gmail.com"
  }
}
"""

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        handle_error('exception occurred!', e)
       
