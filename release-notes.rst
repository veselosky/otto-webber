RELEASE NOTES
=============
Changes that may be backwards incompatible are noted with COMPAT.

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
