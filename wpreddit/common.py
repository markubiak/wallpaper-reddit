import logging
import sys


def exit_msg(message, code=1):
    """Prints an error message and exits the program, with a failure by default"""
    logging.error(message)
    sys.exit(code)
