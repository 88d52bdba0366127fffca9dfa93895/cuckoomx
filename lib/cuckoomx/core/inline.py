#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import logging

from lib.cuckoomx.core.mail import Mail
from lib.cuckoomx.core.databasemx import DatabaseMX
from lib.cuckoomx.common.config import Config

log = logging.getLogger(__name__)

def inline():
    """This is an inline mode of CuckooMX

    In this mode, CuckooMX will capture, extract and analyze mails are
    transferring on traffic. Please not that with this mode, CuckooMX maybe
    affect Mail service, so we recommend using SPAN port.

    NOTE: Please note that this mode is under development
    """
    cfg = Config("cuckoomx")
    enabled = cfg.inline.get("enalbed")

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