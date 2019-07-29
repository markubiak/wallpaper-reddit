import sys


verbose = False


# in - string - messages to print
def log(info):
    """Takes a string and will print it as output if verbose"""
    if verbose:
        print(info)


def set_verbose(val):
    """Sets the global verbosity to True or False"""
    global verbose
    verbose = val


def exit_msg(message, code=1):
    """Prints an error message and exits the program, with a failure by default"""
    print(message)
    sys.exit(code)
