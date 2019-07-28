import sys


verbose = False


# in - string - messages to print
# takes a string and will print it as output if verbose
def log(info):
    if verbose:
        print(info)


def exitmsg(message, code=1):
    print(message)
    sys.exit(code)
