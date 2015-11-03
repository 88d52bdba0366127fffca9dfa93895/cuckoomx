# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import logging

from datetime import datetime
from pymongo import MongoClient

from lib.cuckoomx.common.config import Config

log = logging.getLogger(__name__)

class Database:
    """Database CuckooMX

    This class handles the creation of the cuckoomx database. It also provides
    some functions for interacting with it.
    """

    def __init__(self):
        """Initialize cuckoomx database

        This is a structure of cuckoomx database.
        """

        init_summary_data = {
            "total_mails": 0,
            "total_malwares": 0,
            "total_attachments": 0,
            "total_urls": 0,
            }

        # Status in each mail tell us about this mail, is it done yet?
        #  status = 0: is checking or pending
        #         =-1: is done
        #         > 0: ops, it have some malware?
        #
        # TODO: Should check urls we checked one day ago.
        #
        # NOTE: This init mail data dont be used in anywhere, it is just an
        # example data in database
        init_mails_data = {
            "id": 0,
            "date_created": "2015-02-30 10:00:00",
            "date_ended": "2015-02-30 12:00:00",
            "msg_id": "<863915596.101.1444539469173.JavaMail.zimbra@xxx.com>",
            "status": 5,
            "path": "/opt/zimbra/store/0/3/msg/0/257-12.msg",
            "tasks": [
                {
                    "task_id": 1,
                    "severity": 0,
                    "url": "http://malicious.com",
                    "date_checked": "2015-02-30 10:01:00"},
                {
                    "task_id": 2,
                    "attachment": "malware.exe",
                    "severity": 5,
                    "sha256": "dd6a70b1a22d67c6330dff63717e13ddbf145b8dd026cc2085ad895437b74c2d0a4efbbefeb7f1b79117d9b834e3ed5086881116fd9fa497b5ae5b3261f5c028",
                    "date_checked": "2015-02-30 10:02:00"}],
            "date": "Sun, 30 Feb 2015 10:00:00 +0700 (ICT)",
            "sender": "admin@example.com",
            "sender_ip": "127.0.0.1",
            "subject": "Bonjour, tout le monde",
            "receiver": [
                "user@example.com",
                "tester@example.com"],
            "cc": [
                "user@example.com",
                "tester@example.com"],
            "content_length": "1234",
            "content": "Hello everyone, this is a first mail.",
            }

        self.db = None
        self.connect_database()

        # Initialize data
        if self.is_init() is False:
            self.db["summary"].insert_one(init_summary_data)

    def connect_database(self):
        """Connect to Databases"""
        cfg = Config("cuckoomx")
        host = cfg.mongodb.get("host")
        port = cfg.mongodb.get("port")
        db = cfg.cuckoomx.get("db")

        try:
            conn = MongoClient(host, port)
            self.db = conn[db]
        except:
            log.error("Cannot connect to database Mongodb")

    def is_init(self):
        if self.db["summary"].find_one() is None:
            return False
        return True

    def set_mail_status(self, _id, task_id, status):
        mail = self.db["mails"].find_one({"id": _id}, {"status": 1})

        if status is -1 and mail["status"] is not 0:
            return

        # With every signatures of malware, we will increase status. In the end
        # of each mail, if status is still equal to 0, this is the normal mail
        # and we will update this status to -1 (@para status = -1)
        if status > 0:
            self.db["summary"].update(
                {"id": _id},
                {"$inc": {"total_malwares": 1}})

        self.db["mails"].update(
            {"id": _id},
            {"$inc": {"status": status}})

        self.db["mails"].update(
            {"id": _id, "tasks.task_id": task_id},
            {"$inc": {
                "tasks.$.severity": status}})

        self.db["mails"].update(
            {"id": _id, "tasks.task_id": task_id},
            {"$set": {
                "tasks.$.date_checked": str(datetime.now())}})

    def set_mail_ended(self, _id):
        self.db["mails"].update(
            {"id": _id},
            {"$set": {"date_ended": str(datetime.now())}})

    def add_mail(self, mail):
        self.db["mails"].insert_one({
            "id": self.db["mails"].count(),
            "date_created": str(datetime.now()),
            "date_ended": None,
            "msg_id": mail.get_msg_id(),
            "status": mail.get_status(),
            "path": mail.get_path(),
            "date": mail.date,
            "sender": mail.sender,
            "sender_ip": mail.sender_ip,
            "subject": mail.subject,
            "receiver": mail.receiver,
            "cc": mail.cc,
            "content_length": mail.content_length,
            "content": mail.content,
            "tasks": mail.get_tasks()})

        self.db["summary"].update({}, {"$inc": {
            "total_mails": 1,
            "total_urls": mail.count_urls(),
            "total_attachments": mail.count_attachments()}})
    
    def get_mails_not_done(self):
        mails_not_done = self.db["mails"].find(
            {"status": 0},
            {"id": 1, "tasks.task_id": 1, "tasks.date_checked": 1})

        return mails_not_done

    def url_exist(self, url):
        url_exist = self.db["mails"].find_one({"tasks.url": url})

        if url_exist is None:
            return False
        return True

    def attachment_exist(self, sha256):
        attachment_exist = self.db["mails"].find_one(
            {"tasks.sha256": sha256})

        if attachment_exist is None:
            return False
        return True

    def mail_exist(self, msg_id):
        mail_exist = self.db["mails"].find_one({"msg_id": msg_id})

        if mail_exist is None:
            return False
        return True

    def count_mails(self):
        return self.db["summary"].find_one()["total_mails"]

    def count_malwares(self):
        return self.db["summary"].find_one()["total_malwares"]

    def count_attachments(self):
        return self.db["summary"].find_one()["total_attachments"]

    def count_urls(self):
        return self.db["summary"].find_one()["total_urls"]

    def get_mails_have_malwares(self):
        """Get all mails have malwares, sort by status
        @return: list of mails
        """
        mails = self.db["mails"].find({"status": {"$gt": 0}}).sort([["status", -1]])
        return mails