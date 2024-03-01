
import os
import tomllib
import yaml

# The ConfigManager module loads a TOML based configuration for the
# gerbyRun script and then computes the appropriate gerby.configuration
# constants for use by the Gerby-website code-base, as well as the
# gerbyRun script itself.

import gerby.configuration

# List the known Gerby Constants so that IF they are in the TOML file
# they will be used to over-ride the computed values
gerbyConsts = [
  "COMMENTS",
  "DATABASE",
  "UNIT",
  "DEPTH",
  "PATH",
  "PAUX",
  "TAGS",
  "PDF"
]

# Helper function to compute missing gerby.configuration paths
def computePath(config, aKey, *pathParts, extension=None) :
  newPath = os.path.join(
    config['working_dir'], *pathParts
  )
  if extension : newPath = newPath + '.' + extension
  config[aKey] = newPath

# Load the configuration and update gerby.configuration values
def loadConfig(cmdArgs) :

  # default config
  config = {
    'gerbyConsts' : gerbyConsts,
    'working_dir' : '.',
    'document' : 'document',
    'port' : 5000,
    'host' : "127.0.0.1",
    'github_url' : "https://github.com/stacks/stacks-project",
    'verbose' : cmdArgs['verbose'],
    'quiet' : cmdArgs['quiet']
  }

  # Load the TOML configuration values
  tConfig = {}
  aConfigPath = cmdArgs['configPath']
  try:
    with open(aConfigPath, 'rb') as tomlFile :
      tConfig = tomllib.load(tomlFile)
  except Exception as err :
    print(f"Could not load configuration from [{aConfigPath}]")
    print(repr(err))

  # merge in the TOML config
  for aKey, aValue in tConfig.items() :
    config[aKey] = aValue

  # compute COMMENTS
  if 'comments' not in config :
    computePath(config, 'comments', 'db', 'comments.sqlite' )

  # compute DATABASE
  if 'database' not in config :
    computePath(
      config, 'database', 'db', config['document'], extension='sqlite'
    )

  # compute PATH
  if 'path' not in config : computePath(config, 'path')

  # compute PAUX
  if 'paux' not in config :
    computePath(config, 'paux', config['document'], extension='paux')

  # compute TAGS
  if 'tags' not in config :
    computePath(config, 'tags', config['document'], extension='tags')

  # compute PDF
  if 'pdf' not in config :
    computePath(config, 'pdf', config['document'], extension='pdf')

  # compute absolute path for local templates
  if 'templates_dir' in config :
    templatesDir = config['templates_dir']
    if templatesDir.startswith('~') :
      templatesDir= os.path.expanduser(templatesDir)
    elif templatesDir.startswith('/') :
      pass
    else :
      templatesDir = os.path.abspath(templatesDir)
    config['templates_dir'] = templatesDir

  # Monkey-patch the imported constants in gerby.configuration
  for aConst in gerbyConsts :
    lConst = aConst.lower()
    if lConst in config :
      setattr(gerby.configuration, aConst, config[lConst])

  # report the configuration if verbose
  if config['verbose'] :
    print(f"Loaded config from: [{aConfigPath}]\n")
    print("----- command line arguments -----")
    print(yaml.dump(cmdArgs))
    print("---------- configuration ---------")
    print(yaml.dump(config))
    print("------- gerby configuration ------")
    for aConst in gerbyConsts :
      print(f"{aConst} = {getattr(gerby.configuration, aConst)}")
    print("\n----------------------------------")

  return config
