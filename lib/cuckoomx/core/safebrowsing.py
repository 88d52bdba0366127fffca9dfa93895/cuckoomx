#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import re
import time
import logging
import requests

from lib.cuckoomx.common.config import Config

log = logging.getLogger(__name__)

class SafeBrowsing:
    def __init__(self, key=""):
        cfg = Config("cuckoomx")
        self.key = cfg.safebrowsing.get("key")
        self.client = "cuckoomx"
        self.appver = "0.13.1"
        self.pver = "3.1"

    def __markup(self, url):
        url = url.strip()

        url = url.replace('\t', '')
        url = url.replace('\r', '')
        url = url.replace('\n', '')

        scheme = re.compile("https?\:\/\/", re.IGNORECASE)
        if scheme.match(url) is None:
            url = "http://" + url

        return url

    def lookup(self, urls):
        api_url = "https://sb-ssl.google.com/safebrowsing/api/lookup?client=%s&key=%s&appver=%s&pver=%s" % (self.client, self.key, self.appver, self.pver)
        data = str(len(urls)) + "\n"
        result = []

        for url in urls:
            data += self.__markup(str(url)) + "\n"
        
        response = requests.post(api_url, data=data)
        if response.status_code == 204:
            return True

        for url, line in zip(urls, response.text.splitlines()):
            if line == "ok":
                continue
            result.append(url)
        return result