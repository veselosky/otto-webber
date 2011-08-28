"""Fabric tasks to automate my webserver infrastructure."""

from fabric.api import env, sudo
import fabric.contrib.files as remotefile
import otto.git as git
import otto.web as web
import otto.ubuntu.lucidlynx as server

env['ottohome'] = '/usr/local/share/otto-webber'
env['verbose'] = True
env['otto.git.remote_repo_path'] = "/home/vince/Repo/"

# TODO boto tasks to bring EC2 servers up and down
# TODO Configure an FTP Server.
# TODO Implement disk quotas for users

# TASKS

def install_otto(force_update=False):
    """Install (or upgrade) the otto-webber code on a server.

    Because installing pip requirements can be slow and painful, it is not
    done automatically. Use force_update=True if you need to install or
    upgrade dependencies.
    """
    # Check out otto from a git repo onto the server. Use your own fork if you
    # want.
    otto_repo = env.get('otto_repo', 'https://github.com/veselosky/otto-webber.git')
    git.clone_or_update(env['ottohome'], otto_repo, use_sudo=True)

    # Create a python virtualenv where we will install otto's dependencies.
    venv = env['ottohome']+'/pyvenv'
    if force_update or not remotefile.exists(venv, verbose=env['verbose']):
        sudo('virtualenv --no-site-packages --clear ' + venv)
        sudo('source %s/bin/activate; pip install -Ur %s' % (venv, env['ottohome']+'/requirements.pip') )


# TODO Create & install /usr/local/sbin/adduser.local to customize user on creation.
def new_user(username):
    """Create a new user account."""
    sudo('/usr/sbin/adduser --conf %s/server/adduser.conf %s' % (env['ottohome'], username))


