
import logging
import yaml

from gerby.tools.update import *
from gerby.database import *
import gerby.configuration


# The following code has been adapted from the corresponding code
# (following the line `if __name__ == "__main__":`) in the file
# `gerby/tools/update.py` taken from

# commit: e6c41f5eebcdaedade3dfe7b3dd8a36f967c1336

# commited on: 28/01/24 16:55:16 +0100

# from: https://github.com/gerby-project/gerby-website.git

# It is used (and redistributed) using the MIT license.

# In our use, the `gerby/tools/update.py` command line arguments have been
# replaced by the existence or absence of the corresponding values in the
# `gerbyRun` script's TOML loaded config dictionary.

def updateGerby(config) :

  # setup the basic logger for the tools.update
  logging.basicConfig(stream=sys.stdout)
  log = logging.getLogger(__name__)
  log.setLevel(logging.INFO)

  # monkey-patch this logger back into gerby.tools.update
  gerby.tools.update.log = log

  # create database if it doesn't exist already
  if not os.path.isfile(gerby.configuration.DATABASE):
    for model in [Tag, Proof, Slogan, History, Reference, Commit, Change, Dependency]:
      model.create_table()
    log.info("Created database")

  if not os.path.isfile(gerby.configuration.COMMENTS):
    Comment.create_table()
    log.info("Created COMMENTS database")

  # the information on disk
  tags = getTags()
  files = [f for f in os.listdir(gerby.configuration.PATH) if os.path.isfile(os.path.join(gerby.configuration.PATH, f)) and f != "index"] # index is always created

  if 'noTags' not in config :
    log.info("Importing tags")
    importTags(files)

  if 'noProofs' not in config :
    log.info("Importing proofs")
    importProofs(files)
    removeProofs(files)

  if 'noFootnotes' not in config :
    log.info("Importing footnotes")
    importFootnotes(files)

  if 'noSearch' not in config :
    log.info("Populating the search tables")
    makeSearchTable()

  if 'noParts' not in config :
    log.info("Assigning chapters to parts")
    assignParts()

  if 'noInactivityCheck' not in config :
    log.info("Checking inactivity")
    checkInactivity(tags)

  if 'noDependencies' not in config :
    log.info("Creating dependency data")
    makeDependency()

  if 'noExtras' not in config :
    log.info("Importing history, slogans, etc.")
    importExtras(files)

  if 'noNames' not in config :
    log.info("Importing names of tags")
    nameTags(tags)

  if 'noBibliography' not in config :
    log.info("Importing bibliography")
    makeBibliography(files)

  if 'noCitations' not in config :
    log.info("Managing internal citations")
    makeInternalCitations()

  if 'noTagStats' not in config :
    log.info("Computing statistics")
    computeTagStats()

  if 'noBookStats' not in config :
    log.info("Processing book statistics")
    computeBookStats()
