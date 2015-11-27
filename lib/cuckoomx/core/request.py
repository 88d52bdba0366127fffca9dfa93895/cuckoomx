# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import time
import logging
import requests

from lib.cuckoomx.common.config import Config
from lib.cuckoomx.core.machine import Machine
from lib.cuckoomx.core.databasemx import DatabaseMX

log = logging.getLogger(__name__)

class Request:
    """Handle a way we use request
    """
    def __init__(self):
        """Initialize info for Request"""
        cfg = Config("cuckoomx")
        self.machines = cfg.cuckoomx.get("machines")
        self.api_url = cfg.cuckoo.get("api_url")
        self.maximum_tasks_pending = cfg.cuckoomx.get("maximum_tasks_pending")
        self.dbmx = DatabaseMX()

    def create_url(self, url):
        """Create a url analysis task

        Adds a url to the list of pending tasks. Returns the ID of the newly
        created task.
        """
        task_ids = []
        rest_url = self.api_url + "/tasks/create/url"

        while True:
            if self.dbmx.count_tasks_not_done() < self.maximum_tasks_pending:
                break
            time.sleep(1)

        for machine in self.machines.split(","):
            machine = Machine().get_available_machine(machine)
            request = requests.post(
                rest_url,
                files={"url": ("", url)},
                data={
                  "priority": 1,
                  "machine": machine})

            # Check for request.status_code
            if request.status_code != requests.codes.ok:
                log.warn("Request for url \"%s\" return status_code = %s",
                  url, request.status_code)
                continue

            task_id = request.json()["task_id"]
            if not task_id:
                log.warn("Request for url \"%s\" return task_id = %s",
                  url, task_id)
                return None

            task_ids.append(task_id)

        return task_ids

    def create_file(self, filename, attachment):
        """Create a file analysis task

        Adds a file to the list of pending tasks. Returns the ID of the newly created task.
        """
        task_ids = []
        rest_url = self.api_url + "/tasks/create/file"

        while True:
            if self.dbmx.count_tasks_not_done() < self.maximum_tasks_pending:
                break
            time.sleep(1)

        for machine in self.machines.split(","):
            machine = Machine().get_available_machine(machine)
            request = requests.post(
                rest_url,
                files={"file": (filename, attachment)},
                data={
                  "priority": 1,
                  "machine": machine})

            # Check for request.status_code
            if request.status_code != requests.codes.ok:
                log.warn("Request for file \"%s\" return status_code = %s",
                  filename, request.status_code)
                continue

            task_id = request.json()["task_ids"]
            if not task_id:
                log.warn("Request for file \"%s\" return task_id = %s",
                  filename, task_id)
                return None
        
            task_ids.append(task_id[0])

        return task_ids