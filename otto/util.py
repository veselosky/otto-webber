import codecs
import json
import os.path

from datetime import datetime
from fabric.api import env

########################################################################
# Used everywhere
########################################################################
class paths(object):
    """Class to provide easy access to interpolated paths for Otto."""

    @staticmethod
    def home(*args):
        return os.path.join(env['otto.home'], *args)

    @staticmethod
    def hooks(*args):
        return os.path.join(env['otto.home'], env['otto.path.hooks'], *args)

    @staticmethod
    def repos(*args):
        return os.path.join(env['otto.home'], env['otto.path.repos'], *args)

    @staticmethod
    def sites(*args):
        return os.path.join(env['otto.home'], env['otto.path.sites'], *args)

    @staticmethod
    def virtualenvs(*args):
        return os.path.join(env['otto.home'], env['otto.path.virtualenvs'], *args)

    @staticmethod
    def workspace(*args):
        return os.path.join(env['otto.home'], env['otto.path.workspace'], *args)

    @staticmethod
    def project_dir(*args):
        """Return the path the to project directory (assumed to be the dir containing the fabfile.py)."""
        return os.path.join(os.path.dirname(env['real_fabfile']), *args)

    @staticmethod
    def build_dir(*args):
        return os.path.join(os.path.realpath(env['otto.build_dir']), *args)

    @staticmethod
    def site_dir(*args):
        return os.path.join(env['otto.home'], env['otto.path.sites'], env['otto.site'], *args)


def make_timestamp():
    return datetime.utcnow().strftime('%Y%m%d-%H%M%S')

########################################################################
# Functions for blog.py
########################################################################
def ancestor_of(startfrom, containing):
    """Return the path to the ancestor directory of `startfrom` that contains a file or subdir called `containing`. If not found, returns None."""
    target_dir = startfrom
    while not os.path.exists(os.path.join(target_dir, containing)):
        old_target_dir = target_dir
        target_dir = os.path.dirname(target_dir)
        if target_dir == old_target_dir: # reached root dir
            target_dir = None
            break
    return target_dir


def slurp(filename):
    """Read the entire content of a UTF-8 encoded file as a unicode object"""
    text = u''
    with codecs.open(filename, 'r', 'utf-8') as f:
        text = f.read()
    return text

def dump(text, filename):
    """Write unicode `text` to `filename` with UTF-8 encoding."""
    with codecs.open(filename, 'w', 'utf-8') as f:
        f.write(text)

def strip_private_keys(fromdict):
    """Return a shallow copy of the passed dictionary with "private" keys
    removed (where private keys begin with an underscore)."""
    save_copy = {}
    for k,v in fromdict.iteritems():
        if k.startswith('_'):
            continue
        save_copy[k] = v
    return save_copy

class Encoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'isoformat'):
            return o.isoformat()
        else:
            return super(Encoder, self).default(o)

def json_dump(this, outpath):
    """Save a dict as JSON to the `outfile` using UTF-8 encoding, removing "private" keys."""
    dump(json.dumps(strip_private_keys(this), ensure_ascii=False, cls=Encoder), outpath)

