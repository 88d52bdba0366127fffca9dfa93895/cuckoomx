# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import logging

from datetime import datetime
from pymongo import MongoClient

from lib.cuckoomx.common.config import Config

log = logging.getLogger(__name__)

class DatabaseMX:
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

        # NOTE: This init mail data dont be used in anywhere, it is just an
        # example data in database
        init_mails_data = {
            "id": 0,
            "date_created": "2015-02-30 10:00:00",
            "date_ended": "2015-02-30 12:00:00",
            "msg_id": "<863915596.101.1444539469173.JavaMail.zimbra@xxx.com>",
            "status": 0,
            "highest_malscore": 0,
            "safebrowsing": ["http://malicioussite.net"],
            "path": "/opt/zimbra/store/0/3/msg/0/257-12.msg",
            "tasks": [
                {
                    "task_id": 1,
                    "malscore": 0,
                    "url": "http://malicious.com",
                    "date_checked": "2015-02-30 10:01:00"},
                {
                    "task_id": 4,
                    "malscore": None,
                    "attachment": "malware.exe",
                    "sha256": "dd6a70b1a22d67c6330dff63717e13ddbf145b8dd026cc2085ad895437b74c2d0a4efbbefeb7f1b79117d9b834e3ed5086881116fd9fa497b5ae5b3261f5c028",
                    "date_checked": None}],
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

        self.dbmx = None
        self.connect_database()
        self.init_summary_data = init_summary_data

    def connect_database(self):
        """Connect to Databases"""
        cfg = Config("cuckoomx")
        host = cfg.mongodb.get("host", "127.0.0.1")
        port = cfg.mongodb.get("port", 27017)
        dbmx = cfg.mongodb.get("db", "cuckoomx")

        try:
            conn = MongoClient(host, port)
            self.dbmx = conn[dbmx]
        except:
            log.error("Cannot connect to database Mongodb")

    def drop_database(self):
        """Drop database"""
        cfg = Config("cuckoomx")
        host = cfg.mongodb.get("host", "127.0.0.1")
        port = cfg.mongodb.get("port", 27017)
        dbmx = cfg.mongodb.get("db", "cuckoomx")

        try:
            conn = MongoClient(host, port)
            conn.drop_database(dbmx)
            conn.close()
        except:
            log.warning("Unable to drop MongoDB database: %s", dbmx)

    def is_init(self):
        if self.dbmx["summary"].find_one() is None:
            return False
        return True

    def create_database(self):
        if self.is_init() is False:
            self.dbmx["summary"].insert_one(self.init_summary_data)
            log.debug("Create Database CuckooMX")

    def set_task_malscore(self, _id, task_id, malscore):
        self.dbmx["mails"].update(
            {"id": _id, "tasks.task_id": task_id},
            {"$set": {
                "tasks.$.malscore": malscore,
                "tasks.$.date_checked": str(datetime.now())}})


        if malscore < self.dbmx["mails"].find_one({"id": _id})["highest_malscore"]:
            return
        self.dbmx["mails"].update(
            {"id": _id},
            {"$set": {"highest_malscore": malscore}})

    def set_mail_status(self, _id, status):
        self.dbmx["mails"].update(
            {"id": _id},
            {"$set": {"status": status}})

    def set_mail_ended(self, _id):
        self.dbmx["mails"].update(
            {"id": _id},
            {"$set": {
                "date_ended": str(datetime.now()),
                "status": 1}})

    def add_mail(self, mail):
        _id = self.dbmx["mails"].count()
        cfg = Config("cuckoomx")
        save_storage = cfg.cuckoomx.get("save_storage", "off")

        self.dbmx["mails"].insert_one({
            "id": _id,
            "date_created": str(datetime.now()),
            "date_ended": None,
            "msg_id": mail.get_msg_id(),
            "status": mail.get_status(),
            "highest_malscore": 0,
            "safebrowsing": mail.get_safebrowsing(),
            "path": mail.get_path(),
            "date": mail.date,
            "sender": mail.sender,
            "sender_ip": mail.sender_ip,
            "subject": mail.subject,
            "receiver": mail.receiver,
            "cc": mail.cc,
            "content_length": mail.content_length,
            "content": None,
            "tasks": mail.get_tasks()})

        self.dbmx["summary"].update({}, {"$inc": {
            "total_mails": 1,
            "total_urls": mail.count_urls(),
            "total_attachments": mail.count_attachments()}})
        
        if save_storage is not "off":
            return
        
        self.dbmx["mails"].update(
            {"id": _id},
            {"$set": {"content": mail.content}})

    def get_mails_not_done(self):
        return self.dbmx["mails"].find(
            {"date_ended": None})

    def url_exist(self, url):
        url_exist = self.dbmx["mails"].find_one({"tasks.url": url})

        if url_exist is None:
            return False
        return True

    def attachment_exist(self, sha256):
        attachment_exist = self.dbmx["mails"].find_one(
            {"tasks.sha256": sha256})

        if attachment_exist is None:
            return False
        return True

    def mail_exist(self, msg_id):
        mail_exist = self.dbmx["mails"].find_one({"msg_id": msg_id})

        if mail_exist is None:
            return False
        return True

    def count_mails(self):
        return self.dbmx["summary"].find_one()["total_mails"]

    def count_malwares(self):
        return self.dbmx["summary"].find_one()["total_malwares"]

    def count_attachments(self):
        return self.dbmx["summary"].find_one()["total_attachments"]

    def count_urls(self):
        return self.dbmx["summary"].find_one()["total_urls"]

    def count_tasks_not_done(self):
        return self.dbmx["mails"].count({"tasks": {"date_checked": None}})

    def inc_mails_have_malwares(self):
        """Increase @para total_malwares in database"""
        self.dbmx["summary"].update(
            {}, {"$inc": {"total_malwares": 1}})

    def get_mails_have_malwares(self):
        """Get all mails have malwares, sort by status
        @return: list of mails
        """
        cfg = Config("cuckoomx")
        warning_malscore = cfg.cuckoomx.get("warning_malscore", "2")

        mails = self.dbmx["mails"].find({"$or": [
            {"highest_malscore": {"$gte": int(warning_malscore)}},
            {"safebrowsing": {"$ne": None}}]})

        if mails is None:
            return None
        return mails.sort([("id", -1)])