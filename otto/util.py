import codecs
import os.path

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

