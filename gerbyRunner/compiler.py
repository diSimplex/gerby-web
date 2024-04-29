
import logging
import sys

from lpilGerbyConfig.config import ConfigManager
from gerbyRunner.monkeyPatchConfig import monkeyPatchCompilerConfig
from gerbyRunner.databases import openCreateDatabases

import gerby.configuration
from gerbyRunner.updateManager import updateGerby

def cli() :
  logging.basicConfig(stream=sys.stdout)

  config = ConfigManager(
    chooseCollection=True
  )
  config.loadConfig()
  config.checkInterface({
      'gerby.collections.*.documents.*.dir' : {
      'msg' : 'Documents MUST have a directory speficied'
    },
    'gerby.collections.*.plastexDir' : {
      'msg' : 'Collections MUST have a PlasTex directory specified'
    },
  })

  if not config.cmdArgs['collection'] :
    print("You MUST choose ONE collection for this web server to work!")
    sys.exit(1)

  collectionName = None
  for aCollectionName, aCollectionConfig in config['gerby.collections'].items() :
    if aCollectionName.lower() == config.cmdArgs['collection'] :
      collectionName = aCollectionName
      collectionConfig = aCollectionConfig
      break

  databaseName = None
  for aDatabaseName, aDatabaseConfig in config['tags.databases'].items() :
    if aDatabaseName.lower() == config.cmdArgs['collection'] :
      databaseName = aDatabaseName
      databaseConfig = aDatabaseConfig
      break

  if not collectionName :
    print(f"There is not configuration for the {collectionName} collection")
    sys.exit(1)

  if not databaseName :
    print(f"There is not configuration for the {databaseName} database")
    sys.exit(1)

  config = monkeyPatchCompilerConfig(
    collectionName, collectionConfig,
    databaseName, databaseConfig,
    config.cmdArgs['verbose']
  )

  # This MUST be called AFTER the config has been monkey patched!
  openCreateDatabases()

  # update the gerby website databases
  # which uses the monkey patched gerby.configuration values
  updateGerby(aCollectionName, aCollectionConfig)
