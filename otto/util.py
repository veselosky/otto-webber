import codecs
import datetime
import decimal
import json
import os.path
import time

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
        repo = os.path.join(env['otto.home'], env['otto.path.repos'], *args)
        if args and not repo.endswith('.git'):
            repo += '.git'
        return repo

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
    def local_workspace(*args):
        """Return the path to the project directory (the dir containing the fabfile.py)."""
        return os.path.join(os.path.dirname(env['real_fabfile']), *args)

    @staticmethod
    def build_dir(*args):
        return paths.local_workspace(env['otto.build_dir'], *args)

    @staticmethod
    def site_dir(*args):
        return os.path.join(env['otto.home'], env['otto.path.sites'], env['otto.site'], *args)


def make_timestamp():
    return datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')

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
    """JSON encoder that won't choke on feedparser objects."""
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        elif isinstance(o, time.struct_time):
            return tuple(o)
        else:
            return super(Encoder, self).default(o)


def json_dump(this, outpath):
    """Save a dict as JSON to the `outfile` using UTF-8 encoding, removing "private" keys."""
    dump(json.dumps(strip_private_keys(this), ensure_ascii=False, cls=Encoder, indent=4), outpath)

def json_load(filename):
    """Load a JSON object from a file, given the filename."""
    with codecs.open(filename, 'r', 'utf-8') as f:
        return json.load(f)

