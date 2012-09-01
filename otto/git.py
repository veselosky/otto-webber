# encoding: UTF-8
"""
Utilities and fabric tasks for working with git.

"""
from fabric.api import cd, env, hide, local, run, settings
import fabric.contrib.files as remotefile
import re

from otto.util import paths

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

    # PITA: --tags and --all are mutually exclusive, but I need to push both. >:[
    ensure_remote_repo(target)
    local("git push %s %s" % (branch, remote))
    local("git push --tags %s" % remote)


def local_modifications():
    """Return a list of working copy modifications, parsed from "git status --porcelain".

    Returns None if none found (rather than an empty list).

    Example return value:

        [('M', 'file1.py'), ('A', 'file2.py'), ('D', 'file3.py')]
    """
    with settings(hide('warnings'), warn_only=True):
        # if grep finds something it returns true. We want to invert the logic.
        check = local("git status --porcelain | grep -v ??", capture=True)
        if check.succeeded:
            return re.findall('(?P<status>\w+)\s+(?P<file>.*)', check)
        else:
            return None


def list_tags(pattern=''):
    """List all tags matching `pattern`. Returns a Python list."""
    tags = local("git tag -l '%s' | sort -r" % pattern, capture=True)
    return re.split('\s+', tags)


def clone_or_update(target, repo):
    """Ensure that a directory contains an up-to-date git clone.

    `target` is the directory where the clone should live
    `repo` is the git URL to clone if needed
    `branch` is the branch to check out. Default 'master'.
    """
    if remotefile.exists(target+'/.git', verbose=env.get('verbose', False)):
        with cd(target):
            run('git fetch')
    else:
        run('mkdir -p %s' % target)
        run('git clone %s %s' % (repo, target))


########################################################################
# Utility functions
########################################################################
def get_remote_repo_path():
    """Construct the path of the remote repo."""
    repo = env['otto.site']
    if not repo.endswith('.git'):
        repo = repo+'.git'
    return paths.repos(repo)


def ensure_remote_repo(target):
    """Ensure that the given remote git repository exists"""
    run("mkdir -p %s" % target)
    with cd(target), settings(hide('warnings'), warn_only=True):
        git_check = run("git rev-parse --git-dir")
        if git_check.failed:
            run("git --bare init")

