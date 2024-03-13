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
    sitePackagesDir = f".venv/lib/python{pythonVersion}/site-packages"
    print("Installing JQuery-Bonsai CSS")
    print("----------------------------")
    os.system("git clone --depth=1 https://github.com/aexmachina/jquery-bonsai /tmp/jquery-bonsai")
    os.system(f"cp /tmp/jquery-bonsai/jquery.bonsai.css {sitePackagesDir}/gerby/static/css/")
    os.system("rm -rf /tmp/jquery-bonsai")
    print("----------------------------")
    print("patching gerby website")
    os.system(f"sed -i 's/comments = SqliteDatabase(COMMENTS);/comments = SqliteDatabase(None)/g' {sitePackagesDir}/gerby/database.py")
    print("----------------------------")
    print("patching Bleach Markdown Extension")
    os.system(f"sed -i 's/, md_globals//g' {sitePackagesDir}/mdx_bleach/extension.py")
    os.system(f"sed -i 's/md.safeMode/False/g' {sitePackagesDir}/mdx_bleach/extension.py")
    os.system(f"sed -i \"s/add('bleach', bleach_pp, '>raw_html')/register(bleach_pp, 'bleach', 0)/g\" {sitePackagesDir}/mdx_bleach/extension.py")
    os.system(f"sed -i \"s/styles=self.styles/#styles=self.styles/g\" {sitePackagesDir}/mdx_bleach/postprocessors.py")
    print("----------------------------")
    print("All done!")
