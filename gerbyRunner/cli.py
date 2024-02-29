
import argparse
import logging
import yaml

from waitress import serve

# The following import order is CRITICAL since we are monkey-patching the
# gerby.configuration module's constants.
#
from gerbyRunner.configManager import loadConfig
from gerbyRunner.updateManager import updateGerby
import gerby.application

def cli() :

  # setup the command line arguments
  parser = argparse.ArgumentParser()
  parser.add_argument(
    'configPath',
    help="The path to a TOML file describing how to configure this Gerby-website instance."
  )
  parser.add_argument(
    '-v', '--verbose', action='store_true', default=False,
    help="Be verbose [False]"
  )
  parser.add_argument(
    '-q', '--quiet', action='store_true', default=False,
    help="Be quiet [False]"
  )

  # load the TOML configuration file
  config = loadConfig(vars(parser.parse_args()))

  # update the gerby website databases
  updateGerby(config)

  # Adjust the Waitress logging levels....
  if 'waitress_log_level' in config :
    wLogger = logging.getLogger('waitress')
    wLogger.setLevel(config['waitress_log_level'])

  # Adjust the Flask logging levels....
  # actually I am not sure where/how the Flask logger is created
  # and it does not seem to log to the console....
  #
  # see: https://flask.palletsprojects.com/en/3.0.x/quickstart/#logging
  #
  #gLogger = gerby.application.app.logger
  #print(type(gLogger))
  #gLogger.setLevel(logging.INFO)
  #gLogger.info("starting the gerby webserver

  # start the Gerby Flask App using Waitress
  if not config['quiet'] :
    print("\nYour Waitress will serve you on:")
    print(f"  http://{config['host']}:{config['port']}")
    print("")
  serve(
    gerby.application.app.wsgi_app,
    host=config['host'],
    port=config['port'],
  )
