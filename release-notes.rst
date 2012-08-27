RELEASE NOTES
=============
Changes that may be backwards incompatible are noted with COMPAT.

Release 0.4.0
-------------
* Otto now keeps a copy of your repository at the server.
* web.stage now does a git push to Otto and runs "fab build" at the server.
* COMPAT: otto.git has changed in major ways.
  - create_origin has been removed.
  - clone_or_update no longer accepts the "branch" or "use_sudo" arguments.
  - lots of code added.
* COMPAT: otto.web no longer exports all its fab tasks by default, only the
  essential ones. Makes "fab -l" list less messy.
* COMPAT: Several configuration keys have changed names. Pretty much all keys
  have been moved from "otto.web.*" to "otto.*".
* Tests are very difficult to accomplish in a subdirectory at this stage, since
  the code easily confuses the otto-webber repo with the repo of the code that
  should be using Otto. To be fixed, later.

Release 0.3.0
-------------
* Started keeping release notes, even though the module has not officially been
  "released."
* Now using a consistent versioning scheme. Sorry about that. :/
* COMPAT: From otto.web, removed the `install_vhost` and `remove_vhost` tasks.
  This became problematic when trying to add support for Nginx. Decided to be
  less clever and simply assume that the contents of {{ project }}/etc are
  suitable for direct linking into the system's `/etc` (or `/usr/local/etc`).
  This way I don't have to special case log rotation, cron jobs, or anything
  else. However, it does closely tie a project to the target deployment
  operating system.
* Added `otto.web.install_etc`
* Added `otto.web.service`
* Added `enable_site` and `disable_site` to `otto.web`, a slightly more generic
  replacement for the removed vhost tasks.
* COMPAT: Removed `otto.web.reload_apache` in favor of the more generic and
  useful `otto.web.service`.
* Added `otto.cm.ubuntu.Precise.apache_server` component
* Updates to test directory. Still not automated, but vagrant is easier to use
  now, and the structure of the test site reflects 0.3 conventions.
* Cleaned up lots of cruft that was added during a premature early brainstorm.
