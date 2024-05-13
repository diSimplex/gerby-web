import logging
import os

log = logging.getLogger()

from gerby.database import *
import gerby.configuration

class LPiLToc(BaseModel) :
  entry = ForeignKeyField(Tag)

dbModels = [
  Tag, Proof, Slogan,
  History, Reference,
  Commit, Change,
  Dependency, LPiLToc
]

def openCreateDatabases() :
  # create database if it doesn't exist already
  dbDir = os.path.dirname(gerby.configuration.DATABASE)
  print(dbDir)
  if not os.path.exists(dbDir):
    os.makedirs(dbDir, exist_ok=True)
  db.init(gerby.configuration.DATABASE)
  if not os.path.isfile(gerby.configuration.DATABASE):
    for model in dbModels :
      model.create_table()
    log.info("Created COLLECTIONS database")

  dbDir = os.path.dirname(gerby.configuration.COMMENTS)
  if not os.path.exists(dbDir):
    os.makedirs(dbDir, exist_ok=True)
  comments.init(gerby.configuration.COMMENTS)
  if not os.path.isfile(gerby.configuration.COMMENTS):
    Comment.create_table()
    log.info("Created COMMENTS database")
