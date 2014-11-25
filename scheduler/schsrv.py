#!/usr/bin/env python
import os

from schd import Schd
from schdmon import SchdMon


def scheduler():
    schd = Schd()
    schd.set_monitor(SchdMon())

    schd.scheduler()

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-s", "--settings", dest="settings",
                      help="specify a settings module for project.")

    (options, args) = parser.parse_args()
    if options.settings:
        os.environ["SCHEDULER_SETTINGS"] = options.settings
    scheduler()
