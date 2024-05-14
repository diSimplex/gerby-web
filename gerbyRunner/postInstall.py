import os
import sys

# The following "monkey patches" are required since:

# 1. the existing gerby-website hard codes the comments database before
#    the configuration can be updated.

# 2. The Markdown Bleach Extension is too old and requires updates but is
#    unlikely to be updated (as it looks abandoned)

# 3. we want to install the jquery-bonsia from sources to avoid license
#    issues.

# These patches assume the [PDM PostInstall
# hook](https://pdm-project.org/latest/reference/api/#pdm.signals.post_install)
# as well as the [PDM
# Scripts](https://pdm-project.org/latest/usage/scripts/)

def patches() :
    pythonVersionInfo = sys.version_info
    pythonVersion = f"{pythonVersionInfo[0]}.{pythonVersionInfo[1]}"
    sys.path.append(f".venv/lib/python{pythonVersion}/site-packages")
    # check each path in the sys.path to find where gerby has been installed
    for aPath in sys.path :
      print("Trying:", aPath)
      if os.path.exists(os.path.join(aPath, 'gerby')) :
        sitePackagesDir = aPath
        print("FOUND site-packages:", sitePackagesDir)
        break

    # Now apply our patches
    print("Installing JQuery-Bonsai CSS")
    print("----------------------------")
    os.system("git clone --depth=1 https://github.com/aexmachina/jquery-bonsai /tmp/jquery-bonsai")
    os.system(f"cp /tmp/jquery-bonsai/jquery.bonsai.css {sitePackagesDir}/gerby/static/css/")
    os.system("rm -rf /tmp/jquery-bonsai")
    print("----------------------------")
    print("patching gerby website")
    os.system(f"sed -i '/type = CharField/i \\ \\ doc = CharField(null=True)' {sitePackagesDir}/gerby/database.py")
    os.system(f"sed -i '/pieces = filename.split/a \\ \\ \\ \\ pieces[0] = typeParts[-1]' {sitePackagesDir}/gerby/tools/update.py")
    os.system(f"sed -i '/pieces = filename.split/a \\ \\ \\ \\ typeParts = pieces[0].split(os.sep)' {sitePackagesDir}/gerby/tools/update.py")
    os.system(f"sed -i '/tag.type = pieces/i \\ \\ \\ \\ tag.doc = typeParts[1]' {sitePackagesDir}/gerby/tools/update.py")
    print("----------------------------")
    print("patching Bleach Markdown Extension")
    os.system(f"sed -i 's/, md_globals//g' {sitePackagesDir}/mdx_bleach/extension.py")
    os.system(f"sed -i 's/md.safeMode/False/g' {sitePackagesDir}/mdx_bleach/extension.py")
    os.system(f"sed -i \"s/add('bleach', bleach_pp, '>raw_html')/register(bleach_pp, 'bleach', 0)/g\" {sitePackagesDir}/mdx_bleach/extension.py")
    os.system(f"sed -i \"s/styles=self.styles/#styles=self.styles/g\" {sitePackagesDir}/mdx_bleach/postprocessors.py")
    print("----------------------------")
    print("All done!")


if __name__ == "__main__" :
  patches()