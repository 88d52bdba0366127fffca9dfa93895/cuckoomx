#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import time
import logging

from pymongo import MongoClient

from lib.cuckoomx.common.config import Config
from lib.cuckoomx.core.databasemx import DatabaseMX

log = logging.getLogger(__name__)

def checking():
    """Thread checking() will check a result of Cuckoo"""
    cfg = Config("cuckoomx")
    critical_malscore = cfg.cuckoomx.get("critical_malscore", 6)
    warning_malscore = cfg.cuckoomx.get("warning_malscore", 2)

    dbmx = DatabaseMX()

    # This is not fun for me, I can't find @para malscore in API so I have
    # to use cuckoo database, sorry for the inconvenience
    dbcuckoo = None
    try:
        host = cfg.mongodb.get("host", "127.0.0.1")
        port = cfg.mongodb.get("port", 27017)
        
        conn = MongoClient(host, port)
        dbcuckoo= conn["cuckoo"]
    except:
        log.error("Cannot connect to database Mongodb")

    while True:
        for mail in dbmx.get_mails_not_done():
            if mail["tasks"] is None:
                # This mail don't have anything to check, it is okay.
                # Update status = -1 and continue with a next mail
                dbmx.set_mail_status(mail["id"], -1)
                continue

            # Keep calm and sleep 1s, we will check mail soon :)
            log.debug("Checking mail %s with %s tasks",
                mail["id"], len(mail["tasks"]))

            time.sleep(1)
            check_all_tasks = True

            for task in mail["tasks"]:
                if task["date_checked"] is not None:
                    continue

                task_id = task["task_id"]
                document = dbcuckoo.analysis.find_one(
                    {"info.id": int(task_id)})

                if document is None:
                    # Ops, this task is not done yet, continue with a next task
                    check_all_tasks = False
                    continue

                malscore = document["malscore"]
                if malscore >= critical_malscore:
                    dbmx.inc_mails_have_malwares()
                    log.critical("Mail %s, task %s has malware",
                        mail["id"], task_id)
                elif malscore >= warning_malscore:
                    log.critical("Mail %s, task %s have something wrong",
                        mail["id"], task_id)

                dbmx.set_task_status(
                    mail["id"], task_id=task_id, status=malscore)

            if check_all_tasks:
                dbmx.set_mail_ended(mail["id"])