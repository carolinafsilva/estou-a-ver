import estouaver

import argparse
import daemon
import time
import os

PROGRAM_DESCRIPTION = 'Directory management command-line utility'

DIRECTORY_HELP = 'Specifies which directory to operate on (default=cwd)'
DAEMON_HELP = 'Starts management as a daemon process'
REMOVE_HELP = 'Removes management from the specified directory'

DAEMON_SLEEP_TIME = 300


def get_arguments():
    '''This function returns options parsed from the commandline'''
    parser = argparse.ArgumentParser(
        description=PROGRAM_DESCRIPTION
    )

    parser.add_argument(
        '-dir', '--directory',
        dest='directory',
        action='store',
        metavar='<path>',
        default=os.getcwd(),
        help=DIRECTORY_HELP
    )
    parser.add_argument(
        '-d', '--daemon',
        dest='daemon',
        action='store_true',
        help=DAEMON_HELP
    )
    parser.add_argument(
        '-r', '--remove',
        dest='remove',
        action='store_true',
        help=REMOVE_HELP
    )

    return parser.parse_args()


def main_daemon(args):
    '''This function contains daemon program code'''
    while True:
        # TODO: implement daemon (code that runs periodically)
        print("directory: " + args.directory, "daemon: " +
              str(args.daemon), "remove: " + str(args.remove), sep='\n')
        time.sleep(DAEMON_SLEEP_TIME)


def main(args):
    '''This function contains command-line program code'''
    # TODO: implement command-line functionality
    print("directory: " + args.directory, "daemon: " +
          str(args.daemon), "remove: " + str(args.remove), sep='\n')
    pass


if __name__ == "__main__":
    args = get_arguments()

    if args.daemon:
        log = open(os.getcwd() + '/daemon.log', 'w')
        with daemon.DaemonContext(
            stdout=log,
            stderr=log
        ):
            main_daemon(args)
    else:
        main(args)
