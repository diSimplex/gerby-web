# Running a Gerby website

## Goals

It is a *specific design goal* that a single (linux) server can run
multiple *distinct* instances of the Gerby runner running different
websites *at the same time*.


## Solution

We implement a single "Gerby website runner" tool (`gerbyRun`) which loads
a TOML configuration file describing a specific instance of the
Gerby-website to be run.

Since the Gerby-website code base "hard-codes" (and imports) its own
`configuration.py` file which can not be (statically) altered for
different running instances, the `gerbyRun` tool uses the TOML
configuration file to "monkey-patch" these configuration constants for a
given running instance's requirements.

This `gerbyRun` script implements the (internal) "running" of the
`tools/update.py` script (loaded as a library) and then uses Waitress to
serve the Gebry-website Flask app on a configured `HOST` and `PORT` from
the Gerby document in a configured `WORK_DIR`.

For a typical use case, there will be an additional
"change-monitoring-script" which monitors the files in the `WORK_DIR` and
re-runs the `gerbyRun` tool if any changes are detected. This additional
"change-monitoring-script" might be done using systemd or simply a long
running inotify based command (see below).

## Analysis: Tasks to be done

Based upon
[gerby-project/hello-world](https://github.com/gerby-project/hello-world)
[.travis.yml](https://github.com/gerby-project/hello-world/blob/master/.travis.yml)
there are a number of steps required to run a Gerby website:

1. Get your tags database (flat file of "tag,LaTeX-label")

2. Run [PlasTeX](https://plastex.github.io/plastex/) (with the [Gerby
   plugin](https://github.com/diSimplex/plastex-gerby-plugin)) over your
   document / tags

3. Install and setup the Gerby-website infrastructure, with all required
   static CSS/JS/Python libraries.

```
  # 2) install Gerby
  - git clone https://github.com/gerby-project/gerby-website.git
  - cd gerby-website/gerby/static
  # import jQuery Bonsai
  - git clone https://github.com/aexmachina/jquery-bonsai
  - cp jquery-bonsai/jquery.bonsai.css css/
  # actual install
  - cd ../..
  - pip install -e . # we use -e because we want to change the source files
  - cd ..
```

4. Setup the configuration. *We ignore this step*, since we keep the
   "default" `configuration.py` file unchanged.

   Instead the `gerbyRun` script will "monkey-patch" these configuration
   values using a TOML configuration file loaded by the `gerbyRun` script.

   This allows the same Gerby-Website code base be used to run mulitple
   *different* Gerby-website instances on the same server at the same
   time.

```
  # 3) setup configuration
  - mv configuration.py gerby-website/gerby/configuration.py

```

5. Run the
[gerby-project/gerby-website](https://github.com/gerby-project/gerby-website.git)
[gerby/tools/update.py](https://github.com/gerby-project/gerby-website/blob/master/gerby/tools/update.py)
script to populate the gerby webiste's databases.

```
  # 3) import plasTeX output into database
  - cd gerby-website/gerby/tools
  - python3 update.py
  - cd ../..
```

6. Run the Gerby [Flask](https://flask.palletsprojects.com/en/3.0.x/) app
   using your prefered A/WSGI server.

```
  # 4) run Flask
  - export FLASK_APP=gerby
  - python3 -m flask run &

```

7. Repeat steps (4) and (5) whenever some watched files change. That is,
the "change-monitoring-script" re-runs steps (4)+(5) using `gerbyRun`
whenever it detect changes to the files it monitors.

Tasks (1) and (2) are out of scope for this project, as when, where and
how these two tasks are run will vary greatly between document projects.

Tasks (3), (4), (5), (6) and (7) *are* part of this project, since given the
tags (flat file) and the PlasTeX rendered document, the update and running
of the resulting Gerby website is fairly routine.

Task (3) only needs to be done *once* when the Python packaged Gerby
Runner is itself installed. This is implemented using [PDM's
`post_install`
hook](https://pdm-project.org/latest/usage/hooks/#dependencies-management).

Task (4) is ignored and nothing needs to be done for this step.

Tasks (5) and (6) need to be (re)done whenever the base tags/document is
changed. These tasks should be done by the `gerbyRun` script. This
`gerbyRun` script will run the Gerby tools update script (task (5)) and
then the Waitress/Flask based gerby-webserver app (task (6)).

Task (7), the "change-monitoring-script", (repeatedly) watches for file
changes of the base tags and/or the document changes, and then (re)runs
`gerbyRun` script (tasks (5) and (6)). This step will often be implemented
using systemd (see below).

## Analysis: Required configuration

The basic `configuration.py` file contains the following (global)
constants:

```
# configuration for the website
COMMENTS = "comments.sqlite"
DATABASE = "stacks.sqlite"
UNIT = "section"
DEPTH = 0

# configuration for the import
PATH = "stacks"
PAUX = "stacks.paux"
TAGS = "stacks.tags"
PDF = "stacks.pdf"

```

The `COMMENTS` and `DATABASE` constants are really "private" to the Gerby
website, as these SQLite databases are effectively transient (they are
rebuilt by the tools update script).

The `UNIT` and `DEPTH` constants should probably be `gerbyInit` command
line arguments.

The `PATH`, `PAUX`, `TAGS`, and `PDF` constants should be computable from
location of the base document and its associated tags file.

We will provide `gerbyInit` command line arguments for each of these
constants which can override the "default" computation of these constants
from the "base document directory".

The only *required* argument to the `gerbyInit` command will be the
location/path to the base document directory (as built by PlasTeX).

We will assume that the default values of the configurable constants are:

  - `UNIT` = "section"

  - `DEPTH` = 0

  - `PATH` = <baseDir>/doc

  - `PAUX` = <baseDir>/doc/???.paux

  - `TAGS` = <baseDir>/doc/???.tags

  - `PDF` = <baseDir>/doc/???.pdf


### Runner configuration

We will also need additional configuration:

1. `PORT`

2. `HOST`

3. `WORKING_DIR`

4. `BASE_URL`

5. `GITHUB_URL`

## Questions and Resources

**Q**: Which production server should we use?

**A**: Consider
[Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/index.html)

**Q**: How/when do we (re)run the update script. In particular do we do
this autonomously when a Gerby website is being served on a remote
server?

**A**: We could use:

  - [inotify-tools/inotify-tools](https://github.com/inotify-tools/inotify-tools/wiki)
    (C/C++)

  - [eradman/entr](https://github.com/eradman/entr) (C/C++)

  - [tartley/rerun2](https://github.com/tartley/rerun2) (Bash/inotify)

  - [joh/when-changed](https://github.com/joh/when-changed) (Python)

  - [Watchdog](https://pythonhosted.org/watchdog/) (Python)

  - [vimist/watch-do](https://github.com/vimist/watch-do) (Python)

  - [cespare/reflex](https://github.com/cespare/reflex) (GoLang)

  - [watchexec/watchexec](https://github.com/watchexec/watchexec) (Rust)

**Q**: How do we signal to a running Gerby website to cleanly shutdown?

  - Podman signals to shutdown a container using, SIGTERM and then SIGKILL
  (after a time out) (see:
  [podman-stop](https://docs.podman.io/en/latest/markdown/podman-stop.1.html))

  - [exit cleanly
  examples](https://stackoverflow.com/questions/59893782/how-to-exit-cleanly-from-flask-and-waitress-running-as-a-windows-pywin32-servi)

**A**: *IF* we use Waitress, then the core dispatcher catches the Python
  SystemExit (builtin BaseException) and tells the dispatcher to shutdown,
  providing a clean shutdown. (See lines 137, 171 and 330 of the
  waitress/server.py file).

  This means that we can wrap the actual Gerby server in a Python script
  which traps SIGTERM/SIGKILL and calls sys.exit. This Python script
  should then be responsible for running the tools update script and then
  starting the Waitress server.

  This `gerbyRun` script can be stopped and re-run using one of the above
  Python inotify tools.

**Q**: Can inotify be used inside a Podman container?

**A**: No. You MUST use an *external* process to watch for any changes and
 then issue a podman restart command. (This is essentially the same task
 as when using systemd (see below))

**Q**: Can systemd be used to restart a process on a file change?

**A**: Yes. IF you provide a separate service which watches the files and
  issues a systemd restart command. See:

  - [How to restart service on every configuration change |
  sleeplessbeastie's
  notes](https://sleeplessbeastie.eu/2021/01/20/how-to-restart-service-on-every-configuration-change/)

  - [unix - Restart Systemd service automatically whenever a directory
  changes (any file inside it) - Super
  User](https://superuser.com/questions/1171751/restart-systemd-service-automatically-whenever-a-directory-changes-any-file-ins)
