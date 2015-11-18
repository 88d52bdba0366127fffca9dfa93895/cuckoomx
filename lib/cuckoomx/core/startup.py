# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import logging
import logging.handlers

from lib.cuckoomx.common.constants import CUCKOOMX_ROOT
from lib.cuckoomx.common.utils import create_folders
from lib.cuckoomx.common.exceptions import CuckooOperationalError
from lib.cuckoomx.common.config import Config
from lib.cuckoomx.core.databasemx import DatabaseMX

log = logging.getLogger()

def check_configs():
    """Checks if config files exist.
    @raise CuckooStartupError: if config files do not exist.
    """
    configs = [os.path.join(CUCKOOMX_ROOT, "conf", "cuckoomx.conf")]

    for config in configs:
        if not os.path.exists(config):
            raise CuckooStartupError("Config file does not exist at "
                                     "path: {0}".format(config))

    return True

def create_structure():
    """Creates CuckooMX directories."""
    folders = [
        "log"
    ]

    try:
        create_folders(root=CUCKOOMX_ROOT, folders=folders)
    except CuckooOperationalError as e:
        raise CuckooStartupError(e)

def init_logging():
    """Initializes logging."""
    formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    fh = logging.handlers.WatchedFileHandler(os.path.join(CUCKOOMX_ROOT, "log", "cuckoomx.log"))
    fh.setFormatter(formatter)
    log.addHandler(fh)

    log.setLevel(logging.INFO)

def cuckoomx_clean():
    """Remove database and log of CuckooMX"""
    # Initialize the database connection.
    dbmx = DatabaseMX()

    # Drop all tables.
    dbmx.drop_database()

    # Delete log
    path = os.path.join(CUCKOOMX_ROOT, "log", "cuckoomx.log")
    try:
        os.unlink(path)
    except (IOError, OSError) as e:
        log.warning("Error removing file %s: %s", path, e)