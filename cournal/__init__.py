__version__ = (0, 3, 0, "git")
__versionstring__ = "0.3.0.git"

import sys
# Workaround to make the bundled twisted version work
sys.path.extend(__path__)

from twisted.internet import gtk3reactor
gtk3reactor.install()

from .network import network
from .connectiondialog import ConnectionDialog
from .aboutdialog import AboutDialog
from .mainwindow import MainWindow
from .run import run

__all__ = ["MainWindow", "network", "ConnectionDialog", "AboutDialog", "run"]
