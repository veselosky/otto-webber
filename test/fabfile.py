from fabric.api import env, lcd, local, task as fabtask
import os
import os.path
import otto.blog as blog
import otto.web as web

env['verbose'] = True
env['otto.web.site'] = 'example.com'
env['otto.web.build_dir'] = './build'
env['otto.web.template_dir'] = './templates'
env['otto.blog.entry_template'] = 'entry.html'
env['otto.blog.channel_template'] = 'channel.html'

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
        local('cp -a example.com %s' % env['otto.web.build_dir'])

@fabtask
def clean():
    """make clean"""
    test_root = os.path.dirname(env['real_fabfile'])
    with lcd(test_root):
        local('rm -rf build')

