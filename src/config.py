"""Settings/configuration module. Defines constants to be used in the service"""

import os

# Logging enabled or not
LOGGING = [False, True][1]


def log(where: str, *events):
    """If LOGGING is True, log something to the standard output"""
    if LOGGING:
        print(f'[LOG] {where}: {events}')