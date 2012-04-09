# encoding: UTF-8
"""
Root namespace for Otto Webber.

FIXME Otto currently assumes a specific directory layout. I consider this a
flaw, but I see no easy way around it, and I don't like hard ways. The
assumptions are::

    {{ build_dir }}/etc/apache2/vhost.d/{{ site }} # Apache vhost config file
    {{ build_dir }}/htdocs/ # == DocumentRoot

Deployment tools also assume a Debian-style Apache setup on the server.

"""
__version__ = '0.3.0'

