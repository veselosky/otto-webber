# encoding: UTF-8
"""
Utilities and fabric tasks for working with git.

"""

from fabric.api import cd, env, hide, local, run, settings
import fabric.contrib.files as remotefile
import os
import os.path
from otto.util import paths as home

########################################################################
# Main exported functions
########################################################################
def push(branch='--all', remote="otto"):
    """Pushes to the "otto" remote repo.

    If no "otto" remote exists for the current repo, it is added using the Otto settings.

    If the remote repository has not been created, this will initialize it before pushing.
    """
    # Ensure we're actually in a git working dir
    # This will throw an error if not in a git working dir.
    local("git rev-parse --git-dir")

    target = get_remote_repo_path()

    # Check if the "otto" remote is set up. Add it if not.
    with settings(hide('warnings'), warn_only=True):
        remotes = local("git remote | grep ^%s$"%remote, capture=True)
        if remotes.failed:
            # TODO Figure out how to support multiple protocols, not just ssh
            local("git remote add %s git+ssh://%s%s" % (remote, env.host_string, target))

    ensure_remote_repo(target)
    local("git push %s %s" % (branch, remote))


def clone_or_update(target, repo, branch='master'):
    """Ensure that a directory contains an up-to-date git clone.

    `target` is the directory where the clone should live
    `repo` is the git URL to clone if needed
    `branch` is the branch to check out. Default 'master'.
    `use_sudo` if True, git operations will be performed as superuser.
    """
    if remotefile.exists(target+'/.git', verbose=env['verbose']):
        with cd(target):
            run('git fetch && git checkout %s' % branch)
    else:
        run('mkdir -p %s' % target)
        run('git clone %s %s' % (repo, target))
        with cd(target):
            run('git checkout %s' % branch)


########################################################################
# Utility functions
########################################################################
def get_remote_repo_path():
    """Construct the path of the remote repo."""
    repo = os.path.basename(home.project_dir())
    if not repo.endswith('.git'):
        repo = repo+'.git'
    return home.repos(repo)


def ensure_remote_repo(target):
    """Ensure that the given remote git repository exists"""
    run("mkdir -p %s" % target)
    with cd(target), settings(hide('warnings'), warn_only=True):
        git_check = run("git rev-parse --git-dir")
        if git_check.failed:
            run("git --bare init")


