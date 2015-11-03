#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import time
import fnmatch

from lib.cuckoomx.core.mail import Mail
from lib.cuckoomx.core.database import Database
from lib.cuckoomx.common.config import Config

def offside():
    """This is an offside mode of CuckooMX

    In this mode, CuckooMX will find and analyze mails are stored on hard
    disk (ext .msg). With this mode, CuckooMX will not affect Mail service.
    Please note that CuckooMX need permission to access storage folder of Mail
    service, it don't need write permission
    """
    cfg = Config("cuckoomx")
    enabled = cfg.offside.get("enalbed")

    if enabled is False:
        return False

    storage = cfg.offside.get("storage")

    while True:
        for root, dirnames, filenames in os.walk(storage):
            for filename in fnmatch.filter(filenames, '*.msg'):
                # Keep calm and waiting for Cuckoo, sleep 1s.
                # TODO: should we run fast as much as we can?
                time.sleep(1)
                
                path = os.path.join(root, filename)
                mail = Mail(path)
                mail.parse()

                if mail.is_exist() is True:
                    continue

                if mail.analyze() is False:
                    continue

                # Okay, add it to database
                db = Database()
                db.add_mail(mail)