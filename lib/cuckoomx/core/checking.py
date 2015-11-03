#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import time
import logging

from pymongo import MongoClient

from lib.cuckoomx.common.config import Config
from lib.cuckoomx.core.database import Database

log = logging.getLogger(__name__)

def checking():
    """Thread checking() will check a result of Cuckoo"""
    db = Database()

    # This is not fun for me, I can't find any signature para in API so I have
    # to use cuckoo database, sorry for the inconvenience
    dbcuckoo = None
    try:
        cfg = Config("cuckoomx")
        host = cfg.mongodb.get("host")
        port = cfg.mongodb.get("port")
        conn = MongoClient(host, port)
        dbcuckoo= conn["cuckoo"]
    except:
        log.error("Cannot connect to database Mongodb")

    while True:
        # Keep calm and sleep 2s, we will check mails soon :)
        time.sleep(2)
        
        for mail in db.get_mails_not_done():
            # Keep calm and sleep 1s, we will check mail soon :)
            time.sleep(1)

            # Log this for debug purpose
            log.debug("Checking mail %s with %s tasks",
                mail["id"], len(mail["tasks"]))

            if mail["tasks"] is None:
                # This mail don't have anything to check, it is okay.
                # Update status = -1 and continue with a next mail
                db.set_mail_status(mail["id"], -1)
                continue

            # If this loop have checked all tasks of this mail, so var
            # check_all_tasks still be True and we can sure that this mail is 
            # okay
            check_all_tasks = True

            for task in mail["tasks"]:
                if task["date_checked"] is not None:
                    continue

                cuckoo_task = dbcuckoo.analysis.find_one(
                    {"info.id": task["task_id"]},
                    {"signatures.severity": 1})

                if cuckoo_task is None:
                    # Ops, this task is not done yet, continue with a next task
                    check_all_tasks = False
                    continue

                if not cuckoo_task["signatures"]:
                    # This attachment/url is okay, continue with a next mail
                    continue

                for signature in cuckoo_task["signatures"]:
                    db.set_mail_status(mail["id"],
                        task_id=task["task_id"],
                        status=signature["severity"])

                # Log and alert for admin. In our case, log will be sended
                # to syslog server and we will be alerted from it.
                # TODO: I believe that Cuckoo need a alert function via
                # mail and a tab - something like `malwares tab`
                log.critical("Mail %s have some malware", mail["id"])

            if check_all_tasks:
                # At this time, everything of this mail is okay
                db.set_mail_status(mail["id"], task_id=None, status=-1)
                db.set_mail_ended(mail["id"])