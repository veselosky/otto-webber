from fabric.api import env, lcd, local, sudo, task as fabtask
from fabric.colors import red, green, white
import os
import os.path
import otto.blog as blog
import otto.web as web

env['verbose'] = True
env['use_ssh_config'] = True
env['hosts'] = ['vagrant']
env['user'] = 'vagrant'
env['password'] = 'vagrant'
env['otto.web.site'] = 'example.com'
env['otto.web.build_dir'] = './build/out'
env['otto.web.template_dir'] = './templates'
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
def build():
    """Build the site"""
    build_site_skel()
    blog.build_blog('./blog')


@fabtask
def build_site_skel():
    """First step of build, create the skeleton directory structure."""
    test_root = os.path.dirname(env['real_fabfile'])
    with lcd(test_root):
        local('mkdir -p %s' % env['otto.web.build_dir'])
        local('cp -a example.com/ %s' % env['otto.web.build_dir'])

@fabtask
def clean():
    """make clean"""
    test_root = os.path.dirname(env['real_fabfile'])
    with lcd(test_root):
        local('rm -rf build')

@fabtask
def precise():
    """Testing the Precise class"""
    from otto.cm.ubuntu import Precise
    box = Precise()
    print('initial_setup: ' + green(box.initial_setup))
    (pre, pkgs, post) = box.wsgi_server
    print('wsgi_server: ' + green(' '.join(pkgs)))


@fabtask
def server_setup():
    """Test bootstrapping a server"""
    from otto.cm.ubuntu import Precise
    box = Precise()
    sudo(box.initial_setup)
    sudo(box.install_components(['wsgi_server']))
