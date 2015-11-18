# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import time
import requests

from lib.cuckoomx.common.config import Config

class Machine:
    def get_available_machine(self, machine):
        """ Which machine is available
        @para machine: machine name
        @return: Full VM name is available
        """
        cfg = Config("cuckoomx")
        api_url = cfg.cuckoo.get("api_url")
        rest_url = api_url + "/machines/view/"
        multi = cfg.cuckoomx.get("multi")

        i = 0
        while i <= multi:
            if i == multi:
                # Every machines are not available, wait for them
                time.sleep(1)
                i = 0

            machine_name = machine+str(i)
            request = requests.get(rest_url+machine_name)

            # Check for request.status_code
            if request.status_code != requests.codes.ok:
                continue

            locked = request.json()["machine"]["locked"]
            
            if locked is False:
                return machine_name