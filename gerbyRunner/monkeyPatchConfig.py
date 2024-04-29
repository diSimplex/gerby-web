
import os
import tomllib
import yaml

from lpilGerbyConfig.config import gerbyConsts

# The ConfigManager module loads a YAML based configuration for the
# gerbyRun script and then computes the appropriate gerby.configuration
# constants for use by the Gerby-website code-base, as well as the
# gerbyRun script itself.

import gerby.configuration

# Load the configuration and update gerby.configuration values
# for the webserver

# We MUST monkey patch the following:
#   gerby.configuration.DATABASE
#   gerby.configuration.COMMENTS
#   gerby.configuration.UNIT (used in views/tags.py and views/stacks.py)
#   gerby.configuration.DEPTH (used in views/tags.py)

def monkeyPatchDatabases(collectionName, collectionConfig) :
  print(yaml.dump(collectionConfig))
  plastexDir = collectionConfig['plastexDir']
  dbDir = os.path.join(plastexDir, 'db')
  os.makedirs(dbDir, exist_ok=True)
  htmlDir = os.path.join(plastexDir, 'html')
  os.makedirs(htmlDir, exist_ok=True)

  gerby.configuration.COMMENTS = os.path.join(dbDir, 'comments.sqlite')
  gerby.configuration.DATABASE = os.path.join(dbDir, f"{collectionName}.sqlite")

  return htmlDir

def monkeyPatchWebServerConfig(
  collectionName, collectionConfig,
  databaseName, databaseConfig,
  verbose
) :
  webConfig = collectionConfig['webserver']

  # Monkey patch required gerby.configuration "constants"
  htmlDir = monkeyPatchDatabases(collectionName, collectionConfig)

  gerby.configuration.PATH = htmlDir

  gerby.configuration.UNIT = webConfig['unit']
  gerby.configuration.DEPTH = webConfig['depth']

  # compute absolute path for local templates
  if 'templatesDir' in webConfig :
    templatesDir = webConfig['templatesDir']
    if templatesDir.startswith('~') :
      templatesDir= os.path.expanduser(templatesDir)
    elif templatesDir.startswith('/') :
      pass
    else :
      templatesDir = os.path.abspath(templatesDir)
    webConfig['templatesDir'] = templatesDir

  # report the configuration if verbose
  if verbose :
    print("------- gerby configuration ------")
    for aConst in gerbyConsts :
      print(f"{aConst} = {getattr(gerby.configuration, aConst)}")
    print("\n----------------------------------")

# Load the configuration and update gerby.configuration values
# for the compiler

# We MUST monkey patch the following:
#   gerby.configuration.DATABASE
#   gerby.configuration.COMMENTS
#   gerby.configuration.TAGS (managed by tags website)
#   gerby.configuration.PATH, (needed to collect all "files")
#   gerby.configuration.PAUX (needed for nameTags (which must be altered and run once for each document))
#   gerby.configuration.PDF (only needed for statistics)

def monkeyPatchCompilerConfig(
  collectionName, collectionConfig,
  databaseName, databaseConfig,
  verbose
) :
  webConfig = collectionConfig['webserver']

  # Monkey patch required gerby.configuration "constants"
  htmlDir = monkeyPatchDatabases(collectionName, collectionConfig)

  gerby.configuration.PATH = htmlDir

  gerby.configuration.TAGS = databaseConfig['localPath'].replace('.sqlite', '.tags')

  #gerby.configuration.PAUX = ??


