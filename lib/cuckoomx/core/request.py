# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import logging
import requests

from lib.cuckoomx.common.config import Config

log = logging.getLogger(__name__)

class Request:
    """Handle a way we use request
    """
    def create_url(self, url):
        """Create a url analysis task

        Adds a url to the list of pending tasks. Returns the ID of the newly
        created task.
        """
        cfg = Config("cuckoomx")
        api_url = cfg.cuckoo.get("api_url")
        rest_url = api_url + "/tasks/create/url"
        request = requests.post(
            rest_url,
            files={"url": ("", url)},
            data={
              "priority": 1,
              "machine":"windowsxp"})

        # Check for request.status_code
        if request.status_code != requests.codes.ok:
            log.warn("Request for url \"%s\" return status_code = %s",
              url, request.status_code)
            return False

        task_id = request.json()["task_id"]
        print task_id

        # Check if task_id is None
        if not task_id:
            log.warn("Request for url \"%s\" return task_id = %s",
              url, task_id)
            return False

        return task_id

    def create_file(self, filename, attachment):
        """Create a file analysis task

        Adds a file to the list of pending tasks. Returns the ID of the newly created task.
        """
        cfg = Config("cuckoomx")
        api_url = cfg.cuckoo.get("api_url")
        rest_url = api_url + "/tasks/create/file"
        request = requests.post(
            rest_url,
            files={"file": (filename, attachment)},
            data={
              "priority": 1,
              "machine":"windowsxp"})

        # Check for request.status_code
        if request.status_code != requests.codes.ok:
            log.warn("Request for file \"%s\" return status_code = %s",
              filename, request.status_code)
            return False

        task_id = request.json()["task_id"]
        print task_id

        # Check if task_id is None
        if not task_id:
            log.warn("Request for file \"%s\" return task_id = %s",
              filename, task_id)
            return False

        return task_id