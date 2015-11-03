#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import sys
import logging

from multiprocessing import Process

from lib.cuckoomx.common.config import Config
from lib.cuckoomx.core.offside import offside
from lib.cuckoomx.core.checking import checking
from lib.cuckoomx.core.startup import check_configs
from lib.cuckoomx.core.startup import init_logging
from lib.cuckoomx.core.startup import create_structure

log = logging.getLogger()

def cuckoomx_init():
    check_configs()
    create_structure()
    init_logging()

# We need mode for use signature-devel
#
# NOTE: A persistence_autorun.py is very noisy because it check process READ
# autorun-signature instead of WRITE to it. Skip it.
def main():
    cuckoomx_init()

    try:
        thread_offside = Process(target=offside)
        thread_offside.start()

        thread_checking = Process(target=checking)
        thread_checking.start()
        
        thread_offside.join()
        thread_checking.join()
    except Exception as e:
        log.error("Fail to run CuckooMX: %s", e)

if __name__ == "__main__":
    main()