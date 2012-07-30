#!/usr/bin/python3

import os
import shutil
from distutils.core import setup
import distutils.command.install_scripts
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
        ("/usr/share/icons/hicolor/16x16/apps/", ["icons/hicolor/16x16/apps/cournal.png"]),
        ("/usr/share/icons/hicolor/24x24/apps/", ["icons/hicolor/24x24/apps/cournal.png"]),
        ("/usr/share/icons/hicolor/32x32/apps/", ["icons/hicolor/32x32/apps/cournal.png"]),
        ("/usr/share/icons/hicolor/64x64/apps/", ["icons/hicolor/64x64/apps/cournal.png"]),
        ("/usr/share/icons/hicolor/128x128/apps/", ["icons/hicolor/128x128/apps/cournal.png"]),
        ("/usr/share/icons/hicolor/256x256/apps/", ["icons/hicolor/256x256/apps/cournal.png"]),
        ("/usr/share/icons/hicolor/scalable/apps/", ["icons/hicolor/scalable/apps/cournal.svg"]),
        ("/usr/share/applications/", ["cournal.desktop"])
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
    cmdclass = {"install_scripts": my_install},
)
