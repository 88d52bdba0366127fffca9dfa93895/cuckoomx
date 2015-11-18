#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import os
import sys
import logging
import argparse

from multiprocessing import Process

from lib.cuckoomx.common.config import Config
from lib.cuckoomx.common.constants import CUCKOOMX_VERSION
from lib.cuckoomx.core.offside import offside
from lib.cuckoomx.core.checking import checking
from lib.cuckoomx.core.startup import check_configs
from lib.cuckoomx.core.startup import init_logging
from lib.cuckoomx.core.startup import create_structure
from lib.cuckoomx.core.startup import cuckoomx_clean

log = logging.getLogger()

def cuckoomx_init(quiet=False, debug=False):
    check_configs()
    create_structure()
    init_logging()

    if quiet:
        log.setLevel(logging.WARN)
    elif debug:
        log.setLevel(logging.DEBUG)

def cuckoomx_main():
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--quiet", help="Display only error messages", action="store_true", required=False)
    parser.add_argument("-d", "--debug", help="Display debug messages", action="store_true", required=False)
    parser.add_argument("-v", "--version", action="version", version="You are running CuckooMX {0}".format(CUCKOOMX_VERSION))
    parser.add_argument("--clean", help="Remove database and log of CuckooMX", action='store_true', required=False)
    args = parser.parse_args()

    if args.clean:
        cuckoomx_clean()
        sys.exit(0)

    try:
        cuckoomx_init(quiet=args.quiet, debug=args.debug)

        cuckoomx_main()
    except CuckooCriticalError as e:
        message = "{0}: {1}".format(e.__class__.__name__, e)
        if len(log.handlers):
            log.critical(message)
        else:
            sys.stderr.write("{0}\n".format(message))

        sys.exit(1)