"""
OS-specific data and tasks for Ubuntu. Supported distributions:

* 10.04 (Lucid Lynx): Currently broken, do not use
* 12.04 (Precise Pangolin): Working.
"""
from fabric.api import env, run, settings, sudo, task

class Lucid(object):
    """Options for 10.04 Lucid Lynx"""
    def __init__(self):
        super(Lucid, self).__init__()

    @property
    def base_packages(self):
        """Base for any server"""
        return ['build-essential', 'curl', 'git-core',
         'python-dev', 'python-pip', 'python-virtualenv',
         'screen', 'tree', 'vim-nox'
        ]

    @property
    def apache_server(self):
        """Packages for Apache"""
        return ['apache2-mpm-worker', 'apache2.2-common', 'apache2-suexec-custom',
         'libapache2-mod-fcgid', 'libapache2-mod-wsgi',
         'mysql-client-5.1',
         'python-mysqldb',
         'libjpeg-progs', 'optipng', # image optimization tools for html5boilerplate build
        ]

    @property
    def mysql_server(self):
        """Packages for a MySQL server"""
        return ['mysql-server-5.1', 'mysql-client-5.1']


class Precise(object):
    """Options for 12.04 Precise Pangolin.

    Each of the component properties should return a 3-tuple of (pre, pkgs, post),
    where pkgs is a list of OS packages to be installed, and pre and post are
    scripts to be run before and after the packages are installed. If no pre/post
    is desired, return an empty string, not None. (pre = '')
    """

    @property
    def base_packages(self):
        """Setup basic packages for any server"""
        pre = ''
        post = ''
        pkgs = ['build-essential', 'curl', 'git', 'less', 'screen', 'tree', 'vim-nox', 'wget']
        return (pre, pkgs, post)

    @property
    def apache_server(self):
        """Packages for Apache"""
        pre = ''
        # Some modules are installed but not enabled. I use these.
        post = 'a2enmod include && service apache2 reload'
        pkgs = ['apache2',]
        return (pre, pkgs, post)

    @property
    def python_development(self):
        """Setup for Python development.

        Python development/deployment should always use a virtualenv. I also include
        several pre-built modules that can be a pain to compile due to system library
        dependencies. You can use them by building your virtualenv with
        `--system-site-packages`.
        """
        pre = ''
        post = ''
        pkgs = ['libxml2-dev', 'libxml2-utils', 'python-amqplib',
                'python-anyjson', 'python-crypto', 'python-dateutil',
                'python-dev', 'python-eventlet', 'python-gevent',
                'python-greenlet', 'python-imaging', 'python-libxml2',
                'python-lxml', 'python-pip', 'python-simplejson',
                'python-virtualenv', 'python-yaml', 'virtualenvwrapper']
        return (pre, pkgs, post)

    @property
    def nginx_server(self):
        """Setup for nginx"""
        return '', ['nginx'], '/etc/init.d/nginx start'

    @property
    def nodejs_server(self):
        pre = ''
        pkgs = ['stow']
        post = '''
        mkdir -p /usr/local/Library
        cd /usr/local/Library
        wget http://nodejs.org/dist/v0.8.18/node-v0.8.18-linux-x86.tar.gz
        tar -xzf node-v0.8.18-linux-x86.tar.gz
        stow node-v0.8.18-linux-x86
        '''
        return (pre, pkgs, post)

    @property
    def wsgi_server(self):
        """Setup for WSGI applications"""
        pre = ''
        post = ''
        pkgs = self.python_development[1] + self.nginx_server[1] + ['redis-server']
        return (pre, pkgs, post)

    @property
    def solr_server(self):
        """Solr Server setup.

        Note: This installs Solr the default Solr 1.4, which is now out of date.
        """
        pre = ''
        # jetty depends on openjdk but it isn't declared
        pkgs = ['openjdk-6-jdk', 'jetty', 'solr-common', 'solr-jetty']
        # edit /etc/default/jetty
        # 1. comment out the NO_START directive (Ubuntu disables jetty by default).
        # 2. Set the JAVA_HOME to the right SDK (/etc/alternatives is not enough for jetty)
        post = '''
        sed -i 's/NO_START=1/# NO_START=1/' /etc/default/jetty
        sed -i 's/^#JAVA_HOME=.*/JAVA_HOME=\/usr\/lib\/jvm\/java-6-openjdk-i386/' /etc/default/jetty
        service jetty start || service jetty status
        '''
        return (pre, pkgs, post)

    @property
    def initial_setup(self):
        """Return a script that will update a bare install"""
        return '''sed -i 's/^#\(.*deb.*\) universe/\1 universe/' /etc/apt/sources.list
        aptitude -q=2 -y update
        aptitude -q=2 -y full-upgrade
        '''

    def install_packages(self, packages):
        """Return a command that will install the requested packages."""
        return """aptitude -q=2 -ry install """ + ' '.join(packages)

    def install_components(self, components=[]):
        """Return a script that will install groups of packages (similar to tasksel, but my way)."""
        if isinstance(components, basestring):
            components = [components]
        preinstall, packages, postinstall = self.base_packages
        for component in components:
            pre, pkgs, post = getattr(self, component, ('',[],''))
            preinstall += pre
            packages += pkgs
            postinstall += post
        packages = list(set(packages)) # dedupe, ordering not important
        return "\n".join([preinstall, self.install_packages(packages), postinstall])
