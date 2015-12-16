# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import re
import email
import logging
import hashlib

from lib.cuckoomx.core.request import Request
from lib.cuckoomx.core.databasemx import DatabaseMX
from lib.cuckoomx.core.safebrowsing import SafeBrowsing

log = logging.getLogger(__name__)

class Mail(object):
    """Mail"""

    def __init__(self, path):
        """Initialize
        @param path: path to a file mail.msg
        """
        self.path = path

        self.msg_id = None
        self.msg_ori = None
        self.date = None
        self.sender = None
        self.sender_ip = None
        self.subject = None
        self.receiver = []
        self.cc = None
        self.content = None
        self.content_length = None
        self.status = 0
        self.urls = []
        self.attachments = []
        self.tasks = []
        self.safebrowsing = None

        self.dbmx = DatabaseMX()

    def get_msg_id(self):
        """Get msg_id
        @return: self.msg_id
        """
        return self.msg_id

    def get_status(self):
        """Get status
        @return: self.status
        """
        return self.status

    def get_path(self):
        """Get path
        @return: self.path
        """
        return self.path

    def get_safebrowsing(self):
        """Get safebrowsing
        @return: self.safebrowsing
        """
        return self.safebrowsing

    def get_tasks(self):
        return self.tasks

    def count_urls(self):
        """Get urls
        @return: self.urls
        """
        return len(self.urls)

    def count_attachments(self):
        """Get attachments
        @return: self.attachments
        """
        return len(self.attachments)

    def get_urls(self, content):
        """Get URLs from content of mail
        @para content: get URLs from content
        @return: List URLs
        """
        url_pattern = ("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|"
                      "(?:%[0-9a-fA-F][0-9a-fA-F]))+")

        urls = re.findall(url_pattern, content)
        return urls

    def is_exist(self):
        """Check if this mail exist in database
        @return: True/False
        """
        is_exist = self.dbmx.mail_exist(self.msg_id)
        return is_exist

    def process_urls(self, urls):
        """Process URLs
        @para urls: list of url need to be analyzed
        """
        safebrowsing = SafeBrowsing()
        result = safebrowsing.lookup(urls)
        if result is not True:
            self.safebrowsing = result
        
        for url in urls:
            # Check if this url is exists in our database
            # Should be check it again if we already check this url 1 day ago
            if self.dbmx.url_exist(url):
                continue

            request = Request()
            task_id = request.create_url(url)
            
            if task_id is False:
                return False

            # Okay, add it to task list
            for _id in task_id:
                self.tasks.append({
                    "task_id": _id,
                    "malscore": None,
                    "url": url,
                    "date_checked": None})

    def process_attachments(self, attachments):
        """Process attachments
        @para filenames: list of filenames need to be analyzed
        """
        for attachment in attachments:
            filename = attachment[0]
            payload = attachment[1]

            # Calculate a MD5 hash from payload
            sha256 = hashlib.sha256(payload).hexdigest()

            # Check if hash of file is exists in our database
            if self.dbmx.attachment_exist(sha256):
                continue

            request = Request()
            task_id = request.create_file(filename, payload)
            
            if task_id is False:
                return False

            # Okay, add it to task list
            for _id in task_id:
                self.tasks.append({
                    "task_id": _id,
                    "malscore": None,
                    "attachment": filename,
                    "sha256": sha256,
                    "date_checked": None})
            return True

    def parse(self):
        """Parse mail

        Read a message file from self.path and get informations, urls and/or
        attachments in mail
        """
        msg_file = open(self.path)
        message = email.message_from_file(msg_file)

        self.msg_id = message['message-id']
        self.msg_ori = message.as_string()
        self.date = message['date']
        self.sender = message['from']
        self.sender_ip = message['x-originating-ip']
        self.subject = message['subject']
        self.receiver = message.get_all('to', [])
        self.cc = message.get_all('cc', [])
        self.content = []
        self.content_length = message['content-length']

        for part in message.walk():
            if part.get_content_maintype() == 'multipart':
                # Nothing to do
                continue

            elif part.get_content_maintype() == 'text':
                content = part.get_payload(decode=True)
                self.content.append(content)

                urls = self.get_urls(content)
                self.urls.extend(urls)

            elif part.get_content_maintype() == 'application':
                filename = part.get_filename()
                payload = part.get_payload(decode=True)

                # We can work with an array [filename, payload], so we don't
                # have to stored this file to hard disk
                self.attachments.append([filename, payload])

    def analyze(self):
        """Analyze mail

        After parse mail, foreach url and attachment in it, analyze and add
        it to database
        """
        # We should remove unchecking-task if process have any error
        if self.process_urls(self.urls) is False:
            log.error("%s:Skip this mail", self.msg_id)
            return False

        if self.process_attachments(self.attachments) is False:
            log.error("%s:Skip this mail", self.msg_id)
            return False

        return True