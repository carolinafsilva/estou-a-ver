import argparse
import os


def getArguments():
    parser = argparse.ArgumentParser(
        description='Directory management command-line utility')

    parser.add_argument('-dir', '--directory', action='store', metavar='<path>', default=os.getcwd(),
                        help='Specifies the directory to operate on (default=cwd)')
    parser.add_argument('-r', '--remove', action='store_true',
                        help='Remove the management')
    parser.add_argument('-d', '--daemon', action='store_true',
                        help='Starts as a daemon')
    return parser.parse_args()


def main():
    args = getArguments()
    print(args)


if __name__ == "__main__":
    main()
