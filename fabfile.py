"""Fabric tasks to automate my webserver infrastructure."""

from fabric.api import *

# TODO boto tasks to bring EC2 servers up and down
# TODO Configure an FTP Server.
# TODO Implement disk quotas for users

# 1. Assume Ubuntu 10.10 server base
PACKAGES = {
    'ANYSERVER':
        ['git', 'screen', 'tree', 'vim-nox'],
    'WEBSERVER':
        ['apache2-mpm-worker', 'apache2.2-common', 'apache2-suexec-custom', 'libapache2-mod-fastcgi',
         'mysql-client-5.1',
         'php5-cli', 'php5-fpm', 'php5-adodb', 'php5-gd', 'php5-imagick', 'php5-mysql', 'php5-suhosin', 'php-pear',
         'python-mysqldb',
        ],
    'DATABASE':
        ['mysql-server-5.1', 'mysql-client-5.1'],
}
PACKAGES['FULLSTACK'] = PACKAGES['WEBSERVER'] + PACKAGES['DATABASE']

# TASKS

def setup_server(servertype="FULLSTACK"):
    """Install and configure requisite system packages on a bare server."""
    sudo('apt-get -qy update')
    sudo('apt-get -qy upgrade')
    # Setting frontend to noninteractive prevents prompting for mysql server
    # root password. This means mysql server root password will be empty.
    # TODO Use debconf to set a mysql server root password.
    sudo('DEBIAN_FRONTEND=noninteractive apt-get -qy install ' 
        + ' '.join(PACKAGES['ANYSERVER'] + PACKAGES[servertype.upper()])
        )
    # But until we can configure this beforehand, we'll do it after
    run('mysqladmin -u root password "r00tp4ss"')
    
    # TODO Check out custom software/configs from a git repo into /usr/local somewhere.
    # TODO Add a SKEL dir to custom config, so as not to disturb the system one.

# TODO Task to set up a new user.
def new_user(username):
    """Create a new user account."""
    pass
