"""
OS-specific data and tasks for Ubuntu 10.04 (Lucid Lynx)
"""
from fabric.api import env, run, settings, sudo, task

# TODO Turn PACKAGES into a class so it can be smarter about
# dependencies between package combinations (PHP requires WEBSERVER, etc)
PACKAGES = {
    'ANYSERVER':
        ['build-essential', 'curl', 'git-core',
         'python-dev', 'python-pip', 'python-virtualenv',
         'screen', 'tree', 'vim-nox'
        ],
    'WEBSERVER':
        ['apache2-mpm-worker', 'apache2.2-common', 'apache2-suexec-custom',
         'libapache2-mod-fcgid', 'libapache2-mod-wsgi',
         'mysql-client-5.1',
         'python-mysqldb',
         'libjpeg-progs', 'optipng', # image optimization tools for html5boilerplate build
        ],
    'PHP':
        ['php5-cli', 'php5-cgi', 'php5-adodb', 'php5-gd', 'php5-imagick',
         'php5-mysql', 'php5-suhosin', 'php-pear',
        ],
    'MYSQL':
        ['mysql-server-5.1', 'mysql-client-5.1'],
}
PACKAGES['FULLSTACK'] = PACKAGES['WEBSERVER'] + PACKAGES['MYSQL']

@task
def setup_server(servertype="ANYSERVER", mysqlpassword=None):
    """Install and configure packages on a bare server."""
    sudo('apt-get -qq update')
    sudo('apt-get -qy upgrade')
    # Setting frontend to noninteractive prevents prompting for mysql server
    # root password. This means mysql server root password will be empty.
    # TODO Use debconf to set a mysql server root password.
    SERVER_PACKAGES = set(PACKAGES['ANYSERVER'] + PACKAGES[servertype.upper()])
    sudo('DEBIAN_FRONTEND=noninteractive apt-get -qy install '
        + ' '.join(SERVER_PACKAGES)
        )
    # But until we can configure passwd beforehand, we'll do it after.
    if 'mysql-server-5.1' in SERVER_PACKAGES:
        try:
            mysqlpassword = mysqlpassword or env.mysql.password
        except AttributeError:
            pass
        if mysqlpassword:
            # Note: If the password has already been set, this will fail, hence
            # the "warn only".
            with settings(warn_only=True):
                run('mysqladmin -u root password "%s"' % mysqlpassword)

    # install some python tools at the global level. Because I said so.
    sudo('pip install fabric sphinx')


