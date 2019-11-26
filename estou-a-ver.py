import argparse
import daemon
import os


def get_arguments():
    '''This function returns options parsed from the commandline'''
    parser = argparse.ArgumentParser(
        description='Directory management command-line utility')

    parser.add_argument('-dir', '--directory', action='store', metavar='<path>', default=os.getcwd(),
                        help='Specifies the directory to operate on (default=cwd)')
    parser.add_argument('-r', '--remove', action='store_true',
                        help='Remove the management')
    parser.add_argument('-d', '--daemon', action='store_true',
                        help='Starts as a daemon')
    return parser.parse_args()


def main_daemon(args):
    '''This function contains daemon program code'''
    pass


def main(args):
    '''This function contains command-line program code'''
    pass


if __name__ == "__main__":
        # Get commandline arguments
    args = get_arguments()

    # Define run type
    if args.daemon:
        # Run as a daemon
        with daemon.DaemonContext():
            main_daemon(args)
    else:
        # Run interactively
        main(args)
