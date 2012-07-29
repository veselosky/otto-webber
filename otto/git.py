# encoding: UTF-8
"""
Utilities and fabric tasks for working with git.

"""

from fabric.api import abort, cd, env, local, require, run, sudo, task
import fabric.contrib.files as remotefile
import os
import os.path

# FIXME 0.4 User should not have to care whether remote already exists or not.
# TODO 0.4 Rename create_origin -> push
@task
def push(remote="otto"):
    """Pushes to the "otto" remote repo.

    If no "otto" remote exists for the current repo, it is added using the Otto settings.

    If the remote repository has not been created, this will initialize it before pushing.
    """
    require('otto.git.remote_repo_path')
    # Ensure we're actually in a git working dir
    # This will throw an error if not in a git working dir.
    git_root = local("git rev-parse --git-dir", capture=True)

    # Check if the "otto" remote is set up. Add it if not.
    # FIXME 0.4 Use remote name "otto" instead of origin, ignore other remotes
    # TODO 0.4 Detect and use existing remote "otto" if already present.
    remotes = local("git remote | grep ^otto$", capture=True)
    if remotes:
        abort("This repository already has remotes: "+remotes)

    # Construct the path of the remote repo.
    # FIXME 0.4 Only need to do this at creation. What's the point of passing as arg?
    # TODO 0.4 Move to _create_remote_repo helper func.
    repo = repo or os.path.basename(project_dir)
    if not repo.endswith('.git'):
        repo = repo+'.git'
    remote_path = env['otto.git.remote_repo_path']
    if not remote_path.startswith('/'):
        abort('"remote_repo_path" must be an absolute path (beginning with "/")')

    if remote_path.endswith('/'):
        remote_path = remote_path[:-1]

    target = '/'.join([remote_path, repo])

    # FIXME 0.4 This goes away, pushing to existing repo is legit.
    if remotefile.exists(target):
        abort('Server already has a repo "%s". Use `git remote add origin` instead.' % repo)

    # TODO 0.4 Move to _create_remote_repo helper func.
    run("mkdir -p %s" % target)
    with cd(target):
        run("git --bare init")

    # TODO Figure out how to support multiple protocols, not just ssh
    # FIXME 0.4 Use "otto" not "origin"
    local("git remote add origin git+ssh://%s%s" % (env.host, target))
    local("git push --all --set-upstream origin")

# FIXME 0.4 Nix sudo support, otto should not need root to do this.
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

