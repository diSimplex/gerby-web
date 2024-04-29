# Multi-part Documents

We want to serve multi-part documents. That is documents which have been
PlasTeX'ed individually and then combined into one HTML/Gerby space on the
server.

The current `gerby-webiste` tool assumes a single PlasTeX'ed document.

Alas it also makes a large number of Stack-website assumptions as well.

## Problems

1. The current gerby-website requires a single `*.paux` file. We can
   implement a recursive search for any `*.paux` and load each individually.

2. For database connections, PeeWee uses thread local connections, one per
   thread. It seems that these connections are opened when a new thread is
   created and closed when a thread exits.

   Waitress (the WSGI server) is almost certainly multi-threaded. Do we
   need to control and/or use a thread pool?

3. Should we build the databases outside of the gerby runner and then push
   the files and databases into the running container? Or should we have
   the gerby runner rebuild whenever it is restarted?

   An external build would mean that the container does not need to have
   "extraneous" files/data which could be corrupted.

   An external build would also protect the running server from possible
   failures. This means that the "old" version would continue to be served
   while these errors are fixed.

4. PeeWee, Flask, and Waitress have no intrinsic way to restart
   themselves. We *could* implement such a restart in the gerby runner's
   `cli.py`. However it is not obvious how we might inform the gerby
   runner that it needs to restart.

   It is probably easier to simply restart the container using systemd
   (see design.md)

