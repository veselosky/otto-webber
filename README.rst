Otto Webber - A different kind of web content management system
===============================================================

Otto Webber is a library of fabric tasks, scripts, and functions that help you
manage web sites from the ground up. He will help you with everything from
setting up a new web server to publishing your latest blog post.

.. warning::

    This software is **not** ready for real use. In fact, it hardly does
    anything at all. I am practicing readme-driven development, which means
    this document describes how things should be, not how they are. There
    are more TODOs than lines of code, and even when it works, it will
    probably only work for me.  You should use something else.

How it works (or will work when it does)
========================================

Otto is a system for managing a web site stored in a git repository (although
many of the tools will work fine without git). You can use Otto simply by
adding a fabfile and a configuration file to your git repository.

It *should* work very much like you would expect when manually managing a
content project using git. You create your content in files, check the files
into git, push them to remote repositories, etc.

Using git hooks in the managed repositories, Otto performs transformations
and other tasks on the content you check in. For example, when you check in a
new Markdown file, Otto will automatically convert it to HTML (using the
template you specified), and add it to any index pages you have configured.

Otto does not use a database. He stores all his management data in the file
system, usually in JSON format. Because this data is stored in static files in
your web directory, it effectively becomes an API to your content, given a
properly configured web server (Otto can help you configure your web server
too). Web sites managed by Otto are highly scalable, because they contain
mostly static files.

In fact, you don't even have to install Otto on your web server! You can use
Otto on your development machine to manage a static web site remotely.
However, Otto does include a suite of server-side software to turn your web
site into a true web application. Where possible, server-side code executes in
the background when changes are made, not when site visitors make a request.

