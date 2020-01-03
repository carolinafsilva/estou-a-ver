import estouaver

import argparse
import daemon
import time
import os
import subprocess
import sys


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


def sha256Getter():  # Calcula valores de hash SHA256 para todos os ficheiros e guarda-os num ficheiro .txt
    f_out = open("datab.txt", "w")  # Ficheiro de output
    path = args.directory           # Obter diretoria
    for fname in os.listdir(path):  # Percorrer todos os ficheiros da diretoria
        os.chdir(path)
        with open(fname, "rb") as f:
            output = subprocess.Popen(  # SHA256 do openssl e retornar resultado
                ['openssl', 'dgst', '-sha256', fname], stdout=subprocess.PIPE, universal_newlines=True)
            # Escrever no ficheiro
            f_out.write('%s\n' % (output.stdout.read()))
    f_out.close()


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
