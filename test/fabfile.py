from fabric.api import env, lcd, local, sudo, task as fabtask
from fabric.colors import green
import otto.blog as blog
import otto.git as git
import otto.server as server
import otto.web as web
from otto.util import paths

env['verbose'] = True
env['use_ssh_config'] = True
env['hosts'] = ['vagrant']
env['user'] = 'vagrant'
env['password'] = 'vagrant'
env['otto.home'] = '/home/otto'
env['otto.site'] = 'example.com'
env['otto.build_dir'] = './build/out'
env['otto.template_dir'] = './templates'
env['otto.blog.entry_template'] = 'entry.html'
env['otto.blog.channel_template'] = 'channel.html'

@fabtask
def vagrant_ssh_test_config():
    """Adds the "vagrant" host config to your ~/.ssh/config file

    For recent versions of Vagrant, standard base box no longer supports
    password authentication. This task adds a "vagrant" host config to your
    local `~/.ssh/config` file. It will not replace an existing "vagrant" host,
    so you may need to edit it manually if you do this a lot.
    """
    local('grep -q "Host vagrant" ~/.ssh/config || vagrant ssh-config --host vagrant >> ~/.ssh/config')


@fabtask
def pre_tests():
    """Run the automated test suite"""
    with lcd(paths.project_dir()):
        local('vagrant up') # server
        server_setup() # CM config base box

@fabtask
def run_tests():
    server.setup() # Install otto on server
    git.push() # Upload repository to otto server
    # Sadly, no hooks yet.

@fabtask
def build():
    """Build the site"""
    build_site_skel()
    blog.build_blog('./blog')


def build_site_skel():
    """First step of build, create the skeleton directory structure."""
    with lcd(paths.project_dir()):
        local('mkdir -p %s' % env['otto.build_dir'])
        local('cp -a example.com/ %s' % env['otto.build_dir'])

@fabtask
def clean():
    """make clean"""
    with lcd(paths.project_dir()):
        local('rm -rf build')

@fabtask
def server_setup():
    """Test bootstrapping a server"""
    from otto.cm.ubuntu import Precise
    box = Precise()
    sudo(box.initial_setup)
    sudo(box.install_components(['apache_server']))

@fabtask
def dump():
    from otto.cm.ubuntu import Precise
    box = Precise()
    print('initial_setup: ' + green(box.initial_setup))
    (pre, pkgs, post) = box.wsgi_server
    print('wsgi_server: ' + green(' '.join(pkgs)))
    for key in sorted(env.keys()):
        print "%s = %s" % (key, env[key])


