"""
Travis CI Script for generating libdoc for robotpageobjects.Page and publishing it
"""

from os import getenv
from re import sub
from subprocess import check_output, check_call

if getenv('TRAVIS_PULL_REQUEST'):
    print "Pull request detected, not building docs"

repo = check_output("git config remote.origin.url")
repo = sub(r'^git:', 'https', repo).strip()
deploy_url = sub(r'https://', 'https://%s@' % getenv('GH_TOKEN'), repo)
rev = check_output("git rev-parse HEAD").strip()

check_call("git checkout gh-pages")
check_call("python -m robot.libdoc robotpageobjects.page.Page index.html")
print "Docs built successfully"
check_call("git config user.name '%s'" % getenv('GIT_NAME'))
check_call("git config user.email '%s'" % getenv('GIT_EMAIL'))
check_call("git commit -m 'Built from %s' index.html" % rev)
check_call("git push -q %s gh-pages" % deploy_url)
print "Docs pushed successfully"
