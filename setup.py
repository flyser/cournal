#!/usr/bin/python3

import os
import shutil
import subprocess
from distutils.core import setup
import distutils.command.install_scripts, distutils.command.build, distutils.cmd
from cournal import __versionstring__ as cournal_version

packages = []

twisted_core = [".", "application", "cred", "enterprise", "internet", "manhole", "persisted", "protocols", "python", "spread", "trial"]

for root, subFolders, files in os.walk("cournal"):
    if not root.startswith("cournal/twisted") and "__init__.py" in files:
        packages.append(root.replace("/", "."))

for dir in ["cournal/twisted/" + x for x in twisted_core]:
    for root, subFolders, files in os.walk(dir):
        if "__init__.py" in files:
            packages.append(root.replace("/", "."))


class my_install(distutils.command.install_scripts.install_scripts):
    def run(self):
        distutils.command.install_scripts.install_scripts.run(self)
        for script in self.get_outputs():
            if script.endswith(".py"):
                shutil.move(script, script[:-3])

class build_trans(distutils.cmd.Command):
    """Compile .po files to .mo files"""
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        po_dir = os.path.join(os.path.dirname(__file__), 'i18n/')
        for path, names, filenames in os.walk(po_dir):
            for f in filenames:
                if f.endswith('.po'):
                    lang = f[:-3]
                    src = os.path.join(path, f)
                    dest_path = os.path.join('i18n', lang, \
                        'LC_MESSAGES')
                    dest = os.path.join(dest_path, 'cournal.mo')
                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                    if os.path.exists(dest):
                        src_mtime = os.stat(src)[8]
                        dest_mtime = os.stat(dest)[8]
                        if src_mtime <= dest_mtime:
                            continue
                    print('Compiling %s' % src)
                    subprocess.call(["msgfmt", "--output-file=" + dest, src])
        subprocess.call(["intltool-merge", "--desktop-style", "i18n/", "cournal.desktop.in", "cournal.desktop"])

class build(distutils.command.build.build):
    sub_commands = [('build_trans', None)] + distutils.command.build.build.sub_commands

setup(
    name = "cournal",
    version = cournal_version,
    url = "http://cournal-project.org/",
    download_url = "https://github.com/flyser/cournal/downloads",
    license = "GPLv3+",
    author = "Fabian Henze",
    author_email = "flyser42@gmx.de",
    
    description = "Cournal is a collaborative note taking and journal application using a stylus.",
    long_description = """Cournal allows multiple users to annotate PDF files in real-time.
The goal of this project is a full featured note taking application (like Xournal) or Windows Journal), which allows multiple people to collaborate (like Gobby).

For more information see http://cournal-project.org/""",
    
    packages = packages,
    scripts = ["cournal.py", "cournal-server.py"],
    package_data = {"cournal": ["mainwindow.glade", "connection_dialog.glade", "document_chooser.glade"]},
    data_files = [
        ("share/icons/hicolor/16x16/apps/", ["icons/hicolor/16x16/apps/cournal.png"]),
        ("share/icons/hicolor/24x24/apps/", ["icons/hicolor/24x24/apps/cournal.png"]),
        ("share/icons/hicolor/32x32/apps/", ["icons/hicolor/32x32/apps/cournal.png"]),
        ("share/icons/hicolor/64x64/apps/", ["icons/hicolor/64x64/apps/cournal.png"]),
        ("share/icons/hicolor/128x128/apps/", ["icons/hicolor/128x128/apps/cournal.png"]),
        ("share/icons/hicolor/256x256/apps/", ["icons/hicolor/256x256/apps/cournal.png"]),
        ("share/icons/hicolor/scalable/apps/", ["icons/hicolor/scalable/apps/cournal.svg"]),
        ("share/applications/", ["cournal.desktop"]),
        ("share/locale/de/LC_MESSAGES/", ["i18n/de/LC_MESSAGES/cournal.mo"])
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Framework :: Twisted",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3"
        "Topic :: Communications :: Conferencing",
        "Topic :: Education",
        "Topic :: Office/Business",
        "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
    ],
    cmdclass = {'build': build, 'build_trans': build_trans, "install_scripts": my_install},
)
