# encoding: UTF-8
"""Simple blog manager.

All objects are represented as simple dictionaries. This ensures they can
easily be serialized to and from JSON, the canonical storage format.

Dictionary keys beginning with an underscore are not stored, but are calculated
and inserted by the load routines. Such keys are not gauranteed to exist. Do
not set them yourself.

Datetimes are represented as RFC3339 strings. To manipulate them, you must
convert them yourself. The list of fields containing datetimes is defined in
the module variable `DATETIME_FIELDS`. The software will attempt to parse and
reformat these fields.

"""
# NOTE Filenames from git hook will be relative to project root.

from datetime import datetime
from dateutil import tz, parser as dateparser
from fabric.api import env, lcd, local, task as fabtask
from jinja2 import Environment, FileSystemLoader
import json
import markdown
import os
import os.path
from otto.util import ancestor_of, slurp, dump

DATETIME_FIELDS = ['created', 'date', 'published', 'updated']

def load_entry_markdown(filename):
    """Return an instance of a configured Markdown converter."""
    basename, ext = os.path.splitext(filename)
    channel_dir = ancestor_of(filename, containing='channel.json')
    md = markdown.Markdown(
            extensions=['codehilite', 'extra', 'meta'],
            output_format='html4',
            )
    text = slurp(filename)
    body = md.convert(text)
    metadata = md.Meta
    # Markdown makes every value a list, just in case. I only want lists if the
    # thing claims to be a list.
    entry = {}
    for k,v in metadata.iteritems():
        if len(v) == 1 and not k.endswith('list'):
            entry[k] = v[0]
        else:
            entry[k] = v
        # For any fields containing datetimes, ensure they are fully qualified
        # RFC3339 formatted strings.
        if k in DATETIME_FIELDS:
            default = datetime.now(tz.gettz()).replace(hour=0,minute=0,second=0,microsecond=0)
            dt = dateparser.parse(entry[k], default=default)
            entry[k] = dt.isoformat()

    entry['path'] = os.path.relpath(basename, channel_dir)
    entry['content'] = body

    mtime = datetime.utcfromtimestamp(os.path.getmtime(filename)).isoformat()+'Z'
    entry['_modified'] = mtime
    entry['_filename'] = filename
    entry['_channel'] = load_channel(channel_dir)
    return entry

def load_channel(path):
    """Return a channel dict loaded from the given path"""
    filename = path
    if os.path.isdir(filename):
        filename = os.path.join(filename, 'channel.json')
    if not os.path.exists(filename):
        raise ValueError('Cannot load channel from non-existent path "%s"' % filename)
    channel = json.loads(slurp(filename))
    channel['_filename'] = filename
    return channel

def json_dump(this, outpath):
    """Save a dict as JSON to the `outfile` using UTF-8 encoding, removing "private" keys."""
    save_copy = {}
    for k,v in this.iteritems():
        if k.startswith('_'):
            continue
        save_copy[k] = v
    dump(json.dumps(save_copy, ensure_ascii=False), outpath)


@fabtask
def build_blog(blogdir):
    """Build the blog"""
    blogname = os.path.basename(blogdir)
    entries_for_channel = {} # blog can have multiple channels

    # All the directories and paths we will need for ins and outs
    build_dir = os.path.join(env['otto.web.build_dir'], 'htdocs', blogname)
    template_dir = env['otto.web.template_dir']

    test_root = os.path.dirname(env['real_fabfile'])
    with lcd(test_root):
        local('mkdir -p %s' % build_dir)
        local('cp -a %s %s' % (blogdir+'/', build_dir))

    jinja = Environment(loader=FileSystemLoader(template_dir))

    for thisdir, subdirs, files in os.walk(build_dir):
        for entryfile in files:
            if not entryfile.endswith('.md'):
                continue
            entrypath = os.path.join(thisdir, entryfile)
            outpath, ext = os.path.splitext(entrypath)

            # Load entry, Add to entrylist for its channel
            entry = load_entry_markdown(entrypath)
            channel = entry['_channel']
            entries_for_channel.setdefault(channel['_filename'], [])
            entries_for_channel[channel['_filename']].append(entry)

            # write JSON output
            json_dump(entry, outpath+'.json')

            # Write HTML output (detail page)
            # TODO Allow list of templates, each rendered in turn
            # Entry or channel may specify a template
            template_name = entry.get('template', None) or \
                entry['_channel'].get('entry_template', None) or \
                env['otto.blog.entry_template']
            template = jinja.get_template(template_name)
            context = {'entry':entry, 'channel':entry['_channel']}
            dump(template.render(context), outpath+'.html')

    # Now we've accumulated all the entries. Write the channel indexes.
    for channelfile, entries in entries_for_channel.iteritems():
        outpath = os.path.join(os.path.dirname(channelfile), 'index')
        channel = load_channel(channelfile)

        # sort entries reverse chrono
        entries.sort(key=lambda x: x.get('updated', None) or x.get('date', None) or x.get('_modified', 0), reverse=True)
        channel['entries'] = entries

        # dump index.json
        json_dump(channel, outpath+'.json')

        context = {'channel': channel}

        # render index.html template
        template_name = channel.get('index_template', None) or \
            env['otto.blog.channel_template']
        template = jinja.get_template(template_name)
        dump(template.render(context), outpath+'.html')

        # render FEED template(s)
        feed_template = jinja.get_template('index.atom')
        dump(feed_template.render(context), outpath+'.atom')

