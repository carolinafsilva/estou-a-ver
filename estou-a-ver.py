import argparse
import daemon
import os


def get_arguments():
    '''This function returns options parsed from the commandline'''
    parser = argparse.ArgumentParser(
        description='Directory management command-line utility')

    parser.add_argument(
        '-dir', '--directory',
        dest='directory',
        action='store',
        metavar='<path>',
        default=os.getcwd(),
        help='Specifies which directory to operate on (default=cwd)')
    parser.add_argument(
        '-d', '--daemon',
        dest='daemon',
        action='store_true',
        help='Starts management as a daemon process')
    parser.add_argument(
        '-r', '--remove',
        dest='remove',
        action='store_true',
        help='Removes management from the specified directory')

    return parser.parse_args()


def main_daemon(args):
    '''This function contains daemon program code'''
    pass


def main(args):
    '''This function contains command-line program code'''
    pass


if __name__ == "__main__":
    # Get command-line arguments
    args = get_arguments()

    # Define run type
    if args.daemon:
        # Run as a daemon
        with daemon.DaemonContext():
            main_daemon(args)
    else:
        # Run interactively
        main(args)
