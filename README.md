Course Site Builder
===

Overview
---

These script bring github-pages like functionality to the cs servers. GitHub still serves as the remote repository, but build and deploy is moved to cs servers. Pushing local changes or making modifications through GitHub's ui should trigger a build on the cs server. The built site is then deployed to the course site folder. 

__build_course_site.py__ - commandline utility that builds and deploys course site

1. based on repository name... 
2. pulls changes from a github repo that contains the course site 
3. uses jekyll to build site
4. rsyncs built site to deployment directory
5. emails on exceptions
6. logs last build info to file

__build.cgi__ - cgi script that serves as webhook for course repo on github

1. assuming that course repo is configured to POST to this script on commits (_actually_ push)...
2. extracts repository name
3. calls `build_course_site.py`

Requirements
---
(all available on department's servers)

1. jekyll
2. git
3. cgi / python

Installation
---

1. on server
	1. place `build.cgi` in cgi-bin (see helpdesk directions on proper permissions and location)
	2. place `build_course_site.py` in any directory on server; just make sure it's executable 
2. on github
	1. create new repository with name in this format: `csci-ua.0123-fall2016-009`
	2. under settings, add webhook for push only... the url should point to the location of `build.cgi`
3. on server (again)
	1. clone your repository
	2. modify the default values in `build_course_site.py` to use the appropriate values for:
		* `DEFAULT_STAGING_PATH` - directory that contains your cloned repo
		* `DEFAULT_COURSES_BASE_PATH` - absolute path to directory that contains course all course sites w/ out semeseter
		* `DEFAULT_SERVER` - smtp server for sending error emails
	3. fill in the blank values in `build.cgi` under the first `TODO`
		* `cmd` - absolute path to location of build_course_site.py
		* `erroremail` - append email address of where error messages should be sent
		* `sender` - append eemail address of sender
		* `log` - absolute path to location of build logs

Usage
---

`build_course_site.py` can be used as a standalone commandline utility (independent from the cgi script) to pull, build and deploy your site:

```
build_course_site.py [-h] [--staging STAGING] [--target TARGET]
                            [--erroremail ERROREMAIL] [--sender SENDER]
                            [--server SERVER] [--log LOG]
                            repo_name
```
		
To use with the webhook:

1. make a change to your repo and push it
2. you can find the output of the webhook in github's ui through the webhook page under settings
3. the cgi script should always respond with the post data that it received from github
4. ...the status of the webhook should have a green checkmark
5. note that the cgi-script should give back a response even before the site is built

