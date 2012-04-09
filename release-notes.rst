RELEASE NOTES
=============
Changes that may be backwards incompatible are noted with COMPAT.

Release 0.3.0
-------------
* Started keeping release notes, even though the module has not officially been "released."
* Now using a consistent versioning scheme. Sorry about that. :/
* COMPAT: From otto.web, removed the `install_vhost` and `remove_vhost` tasks.
    This became problematic when trying to add support for Nginx. Decided to be less clever
    and simply assume that the contents of {{ project }}/etc are suitable for direct linking
    into the system's `/etc` (or `/usr/local/etc`). This way I don't have to special case
    log rotation, cron jobs, or anything else.
* COMPAT: Removed otto.web.reload_apache in favor of the more generic and useful otto.web.service.
* Added otto.web.install_etc
* Added otto.web.service