"""
Travis CI Script for generating libdoc for robotpageobjects.Page and publishing it
"""

from os import getenv, chdir
from re import sub
from subprocess import check_output, check_call
from tempfile import mkdtemp
from shutil import rmtree

if getenv('TRAVIS_REPO_SLUG') != 'ncbi/robotframework-pageobjects':
    print "Repo is a fork, not building docs"
    exit()

if getenv('TRAVIS_BRANCH') != 'master':
    print "Branch is not master, not building docs"
    exit()

if getenv('TRAVIS_PULL_REQUEST') != 'false':
    print "Pull request detected, not building docs"
    exit()

repo = check_output("git config remote.origin.url", shell=True)
repo = sub(r'^git:', 'https:', repo).strip()
deploy_url = sub(r'https://', 'https://%s@' % getenv('GIT_TOKEN'), repo)
deploy_branch = 'gh-pages'
rev = check_output("git rev-parse HEAD", shell=True).strip()

dir = mkdtemp()
check_call("git clone --branch %s %s %s" % (deploy_branch, repo, dir), shell=True)
chdir(dir)
check_call("python -m robot.libdoc robotpageobjects.Page index.html", shell=True)
print "Docs built successfully"
check_call("git config user.name '%s'" % getenv('GIT_NAME'), shell=True)
check_call("git config user.email '%s'" % getenv('GIT_EMAIL'), shell=True)
check_call("git commit -m 'Built from %s' index.html" % rev, shell=True)
check_call("git push -q %s %s" % (deploy_url, deploy_branch), shell=True)
chdir(getenv('TRAVIS_BUILD_DIR'))
rmtree(dir)
print "Docs pushed successfully"
