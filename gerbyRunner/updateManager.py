
import glob
import logging
import markdown
import yaml

from gerby.tools.update import *
from gerby.database import *
import gerby.configuration

from gerbyRunner.databases import LPiLToc, LPiLMD

def clearLpilToc() :
  if LPiLToc.table_exists() : LPiLToc.drop_table()
  LPiLToc.create_table()

def addLpilTocEntries(docDir, tags, log) :
  for anAuxPath in glob.iglob("**/*.aux", root_dir=docDir, recursive=True) :
    anAuxPath = os.path.join(docDir, anAuxPath)
    with open(anAuxPath) as auxFile :
      for aLine in auxFile :
        for aLine in auxFile :
          if aLine.startswith("\\newlabel") :
            aLabel = aLine.split("{")[1].rstrip("}")
            try :
              theTag = Tag.get(Tag.label == aLabel)
              anEntry = LPiLToc.create(entry=theTag)
              anEntry.save()
            except DoesNotExist as err :
              log.warning(repr(err))

def clearLpilMd() :
  if LPiLMD.table_exists() : LPiLMD.drop_table()
  LPiLMD.create_table()

def addLpilMdEntry(docName, docConfig, log) :
  docDir = docConfig['dir']
  readmePath = os.path.join(docDir, 'Readme.md')
  readmeHtml = ""
  if os.path.isfile(readmePath) :
    with open(readmePath) as readmeFile :
      readmeHtml = markdown.markdown(readmeFile.read())
  todoPath = os.path.join(docDir, 'ToDo.md')
  todoHtml = ""
  if os.path.isfile(todoPath) :
    with open(todoPath) as todoFile :
      todoHtml = markdown.markdown(todoFile.read())
  anEntry = LPiLMD.create(
    doc=docName,
    readme=readmeHtml,
    todo=todoHtml
  )
  anEntry.save()

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

def updateGerby(collectionName, collectionConfig) :
  # setup the basic logger for the tools.update
  log = logging.getLogger(__name__)
  log.setLevel(logging.INFO)

  # monkey-patch this logger back into gerby.tools.update
  gerby.tools.update.log = log

  # get the tag information
  tags = getTags()
  #print(yaml.dump(tags))

  # get the list of relevant files..
  #
  # We simulate the following list compression:
  # files = [f for f in os.listdir(gerby.configuration.PATH) if
  # os.path.isfile(os.path.join(gerby.configuration.PATH, f)) and f !=
  # "index"] # index is always created

  os.chdir(gerby.configuration.PATH)
  files = []
  for aFile in glob.glob('**', recursive=True) :
    if not os.path.isfile(aFile) : continue
    if aFile.endswith('index') : continue
    files.append(aFile)
  #print(yaml.dump(files))


  if 'noTags' not in collectionConfig :
    log.info("Importing tags")
    importTags(files)

  if 'noProofs' not in collectionConfig :
    log.info("Importing proofs")
    importProofs(files)
    removeProofs(files)

  if 'noFootnotes' not in collectionConfig :
    log.info("Importing footnotes")
    importFootnotes(files)

  if 'noSearch' not in collectionConfig :
    log.info("Populating the search tables")
    makeSearchTable()

  clearLpilToc()
  clearLpilMd()

  origPath = gerby.configuration.PATH
  for aDocumentName, aDocumentConfig in collectionConfig['documents'].items() :
    print("------------------------------------------")
    print(f"Working on: [{aDocumentName}]")
    #print(yaml.dump(aDocumentConfig))
    gerby.configuration.PATH = os.path.join(origPath, aDocumentName)
    #print(gerby.configuration.PATH)
    gerby.configuration.PAUX = os.path.splitext(os.path.join(
      aDocumentConfig['dir'],
      aDocumentConfig['doc']
    ))[0]+'.paux'
    #print(gerby.configuration.PAUX)

    if 'noMarkdown' not in collectionConfig :
      log.info("Adding markdown")
      addLpilMdEntry(aDocumentName, aDocumentConfig, log)

    if 'noLPiLToc' not in collectionConfig :
      log.info("Adding LPiL TOC entries")
      addLpilTocEntries(aDocumentConfig['dir'], tags, log)

    # need to NOT drop the Part table... but rather combine them across
    # fingerPieces / diSimplex-chapters

    if 'noParts' not in collectionConfig :
      log.info("Assigning chapters to parts")
      assignParts()

    # each fingerPiece / diSimplex-chapter has a collection of names which
    # each individually get updated into the database.

    if 'noNames' not in collectionConfig :
      log.info("Importing names of tags")
      nameTags(tags)

    # We really need to figure out how to combine these statistics from
    # each fingerPiece / diSimplex-chapter

    #if 'noBookStats' not in collectionConfig :
    #  log.info("Processing book statistics")
    #  computeBookStats()

  print("------------------------------------------")
  gerby.configuration.PATH = origPath

  if 'noInactivityCheck' not in collectionConfig :
    log.info("Checking inactivity")
    checkInactivity(tags)

  if 'noDependencies' not in collectionConfig :
    log.info("Creating dependency data")
    makeDependency()

  if 'noExtras' not in collectionConfig :
    log.info("Importing history, slogans, etc.")
    importExtras(files)

  if 'noBibliography' not in collectionConfig :
    log.info("Importing bibliography")
    makeBibliography(files)

  if 'noCitations' not in collectionConfig :
    log.info("Managing internal citations")
    makeInternalCitations()

  if 'noTagStats' not in collectionConfig :
    log.info("Computing statistics")
    computeTagStats()

  db.close()