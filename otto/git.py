# encoding: UTF-8
"""
Utilities and fabric tasks for working with git.

"""

from fabric.api import abort, cd, env, local, puts, require, run, sudo, task
import fabric.contrib.files as remotefile
import os
import os.path

@task
def create_origin(repo=None):
    """Create upstream origin repo from current local one."""
    require('otto.git.remote_repo_path')
    # Ensure we're actually in a git working dir
    project_dir = os.getcwd()
    while not os.path.exists(os.path.join(project_dir, '.git')):
        old_project_dir = project_dir
        project_dir = os.path.dirname(project_dir)
        if project_dir == old_project_dir: # reached root dir
            project_dir = None
            abort("Unable to locate a .git directory")

    # Ensure we don't already have remotes set up.
    remotes = local("git remote", capture=True)
    if remotes:
        abort("This repository already has remotes: "+remotes)

    # Construct the path of the remote repo.
    repo = repo or os.path.basename(project_dir)
    if not repo.endswith('.git'):
        repo = repo+'.git'
    remote_path = env['otto.git.remote_repo_path']
    if not remote_path.startswith('/'):
        abort('"remote_repo_path" must be an absolute path (beginning with "/")')

    if remote_path.endswith('/'):
        remote_path = remote_path[:-1]

    target = '/'.join([remote_path, repo])

    if remotefile.exists(target):
        abort('Server already has a repo "%s". Use `git remote add origin` instead.' % repo)

    run("mkdir -p %s" % target)
    with cd(target):
        run("git --bare init")

    # TODO Figure out how to support multiple protocols, not just ssh
    local("git remote add origin git+ssh://%s%s" % (env.host, target))
    local("git push --all --set-upstream origin")


def clone_or_update(target,repo,branch='master',use_sudo=False):
    """Ensure that a directory contains an up-to-date git clone.

    `target` is the directory where the clone should live
    `repo` is the git URL to clone if needed
    `branch` is the branch to check out. Default 'master'.
    `use_sudo` if True, git operations will be performed as superuser.
    """
    action = sudo if use_sudo else run
    if remotefile.exists(target+'/.git', verbose=env['verbose']):
        with cd(target):
            action('git fetch && git checkout %s' % branch)
    else:
        action('mkdir -p %s' % target)
        action('git clone %s %s' % (repo, target))
        with cd(target):
            action('git checkout %s' % branch)

def check_settings():
    """Just a test to see if otto has settings"""
    if isinstance(env.otto, dict):
        puts("ok env.otto does not throw error")
    else:
        puts("not ok I did something wrong: "+env.otto)

    print env.otto['git']
