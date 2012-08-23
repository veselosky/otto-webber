# encoding: UTF-8
"""
Otto Webber - Web Server Automation
===================================
Otto Webber is a library of tools to help you manage web sites that are stored
in git repositories.

Assumptions and Prerequisites
-----------------------------
Deployment tools assume a Debian-style setup on the server. Some things may not
work correctly if you use a server system that behaves differently from Debian.

Python is a requirement. I use Python 2.7. Things should run fine with Python
2.5+, but at the moment I'm not testing with versions other than 2.7. Once the
API has stabilized and automated testing has been added, I'll fix any version
bugs. You will need Python installed both on your local system and on your
server.

Documentation assumes you are using virtualenvwrapper. Just do it.

Using Otto Webber
-----------------
First, create a git repository to hold your web site. Then, create your web
site. Check it in.

Add a `requirements.txt` to your repo, listing the version of Otto you want to
use, plus any other Python libraries that your build may require.

Add a `fabfile.py` to your repo. Otto requires that you set the following
variables in fabric's `env`.

* `otto.build_dir` - the local path where your build task will place its output.
* `otto.site` - the domain name of the web site in this repo. Used in file
  paths and templates.

Other env variables you may care about have default values, but may be overridden.

* `otto.home` - the path where the Otto environment is set up on the server.
  Defaults to `/usr/local/share/otto`.
* `otto.httpserver` - which web server you run. Defaults to "apache2". Any web
  server that follows Debian setup conventions should work. "nginx" is known to
  work.

In your fabfile, create a `build` task that assembles your web site as it will
exist on the server into the `otto.build_dir`. Test it locally to ensure
everything works. You can add the build dir to your .gitignore, you won't need
to check the completed files into git.

When you're ready, merge your changes into your local staging branch ("master"
by default). Then execute `fab otto.push` to upload your site to Otto's
server-side repository. Otto will create a tag and push your staged changes to
the server. Git hooks on the server will see the change and deploy your site to
the staging area where you can give it one final check.

When you are ready, execute `fab web.deploy`. Otto will rsync your staged site
to the deployment area.
"""
__version__ = '0.4.0'

from fabric.api import env

DEFAULT_CONFIG = {
    'otto.home': '/usr/local/share/otto',
    'otto.path.deployments': 'deployments', # relative to otto.home
    'otto.path.hooks': 'hooks', # relative to otto.home
    'otto.path.repos': 'repos', # relative to otto.home
    'otto.path.sites': 'sites', # relative to otto.home
    'otto.path.virtualenvs': 'virtualenvs', # relative to otto.home
    'otto.path.workspace': 'workspace', # relative to otto.home
    'otto.requirements_file': 'requirements.txt',
    'otto.httpserver': 'apache2',
    'otto.git.staging_branch': 'master',
    }
for k, v in DEFAULT_CONFIG.iteritems():
    env.setdefault(k, v)

# TODO 0.4 Need to create hook scripts that do the actual build/deploy/rollback
