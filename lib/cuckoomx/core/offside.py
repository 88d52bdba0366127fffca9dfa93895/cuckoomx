#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import time
import fnmatch
import logging

from lib.cuckoomx.core.mail import Mail
from lib.cuckoomx.core.databasemx import DatabaseMX
from lib.cuckoomx.common.config import Config

log = logging.getLogger(__name__)

def offside():
    """This is an offside mode of CuckooMX

    In this mode, CuckooMX will find and analyze mails are stored on hard
    disk (ext .msg). With this mode, CuckooMX will not affect Mail service.
    Please note that CuckooMX need permission to access storage folder of Mail
    service, it don't need write permission
    """
    cfg = Config("cuckoomx")
    enabled = cfg.offside.get("enalbed")
    store = cfg.offside.get("store")

    if enabled is False:
        return False
    
    while True:
        nothing_to_check = True
        for root, dirnames, filenames in os.walk(store):
            for filename in fnmatch.filter(filenames, '*.msg'):
                path = os.path.join(root, filename)
                mail = Mail(path)
                mail.parse()

                log.debug("Parsing mail %s at %s", mail.get_msg_id(), path)

                if mail.is_exist() is True:
                    continue

                if mail.analyze() is False:
                    continue

                # Okay, add it to database
                dbmx = DatabaseMX()
                dbmx.add_mail(mail)

                nothing_to_check = False
                log.debug("Add mail %s to database", mail.get_msg_id())

        if nothing_to_check:
            time.sleep(1)