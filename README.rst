RETIRED
========

This software is no long used or maintained. It remains here for historical
purposes only. For those interested, I moved to using Ansible for infrastructure
automation, and various other tools for static site generation (I seem to pick
a new tool for every site).

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

Current state as of 0.3.0
========================================
Most of what you see here is in a purely experimental stage. The only really
useful bit is `otto.web`, a library of Fabric tasks used to automate web
deployments. The author uses it to deploy several production web sites. The
author also uses `otto.cm` to help configure the web server where the sites are
deployed. However, it's kindergarten stuff and probably not useful to anyone
but Vince.

The deployment code in `otto.web` is only suitable for static web sites. You
are responsible for creating your own "build" task that will collect a local
directory as you would like it to appear on the server. Otto then provides fab
tasks for deploying to the server (or rolling back to a previous deployment).
This makes it fairly simple to maintain a static HTML or Sphinx-built site in a
git repo, requiring only a fabfile with a few lines of code to run the build.

Roadmap
========================================
**Git push deployments.** Add Git hooks that will allow Otto to take action on
changes pushed to the repo. This should allow a smoother deployment path more
like Heroku, where "deploy" and "push" are synonymous. This requires server
side code and per-site virtualenv support, so that Otto can run the build tasks
at the server.

**Incremental deployment.** Add the capability to deploy only files that have
changed since the previous deployment, rather than rebuilding/redeploying the
entire site. This will be necessary for large, rapidly growing sites.

**Self-updating applications.** Add the ability for a server-side process to
add content to the repository for a site, triggering an incremental deploy.
This would allow for building a web-based CMS or a cron-based aggregator using
Git as the backing store.






