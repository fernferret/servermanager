#!/usr/bin/env python

import argparse

class ServerSync(object):
    def __init__(self):
        pass

def main():
    print "Main!"
    parser = argparse.ArgumentParser(description='Sync files from one server folder to another.')
    parser.add_argument('from', metavar='FROM',
                       help='The server to use as the gold copy.')
    parser.add_argument('to', metavar="TO",
                       help='The server to syncronize with the gold copy.')
    
    args = parser.parse_args()
    print(args.accumulate(args.integers))

if __name__ == "__main__":
    main()
