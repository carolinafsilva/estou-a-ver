# ------------------------------------------------------------------------------
# Libraries

import subprocess
import argparse
import daemon
import time
import sys
import os

# ------------------------------------------------------------------------------
# Global Variables

DATABASE_NAME = "database.db"

DAEMON_SLEEP_TIME = 300

# ------------------------------------------------------------------------------
# Strings

PROGRAM_DESCRIPTION = 'Directory management command-line utility'

DIRECTORY_HELP = 'Specifies which directory to operate on (default=cwd)'
DAEMON_HELP = 'Starts management as a daemon process'
REMOVE_HELP = 'Removes management from the specified directory'

# ------------------------------------------------------------------------------
# Function Definitions


def get_files(directory):
    '''This function returns a list of files from the directory'''
    return [f for f in os.listdir(directory) if os.path.isfile(f)]


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


def SHA256(filename):
    '''This function returns the SHA256 of the filename'''
    output = subprocess.Popen(
        ['openssl', 'dgst', '-sha256', filename],
        stdout=subprocess.PIPE,
        universal_newlines=True)
    return output.stdout.read()


def AES_128_CBC(filename, hex_key, iv):
    '''This function encrypts the filename with AES-128-CBC'''
    subprocess.Popen(
        ['openssl', 'enc', '-aes-128-cbc', '-K',
            hex_key, '-in', filename, '-out', filename, '-iv', iv],
        stdout=subprocess.PIPE,
        universal_newlines=True)


def create_database(args):
    '''This function calculates hashes SHA256 for all files inside a directory and saves them to the database'''
    # Open database file
    db = open(DATABASE_NAME, "w")
    # Go to directory
    os.chdir(args.directory)
    # For each file in directory
    for filename in get_files(args.directory):
        # Get hash
        output = SHA256(filename)
        # Write to database
        db.write(output)
    db.close()


# def directory_monitor():
#     '''This function checks for changes inside directory'''
#     # guardar lista de ficheiros na observação atual
#     current = get_managed_files()
#     # Ver se algum ficheiro foi adicionado
#     adicionado = [f for f in current if not f in managed_files]
#     # Ver se algum ficheiro foi removido
#     removido = [f for f in managed_files if not f in current]
#     if adicionado:
#         print("Adicionado: ", adicionado)
#     if removido:
#         print("Removido: ", removido)
#     managed_files = current
#     db_write_hashes()


def main_daemon(args):
    '''This function contains daemon program code'''
    # Debug info
    print("directory: " + args.directory, "daemon: " +
          str(args.daemon), "remove: " + str(args.remove), sep='\n')
    # TODO: implement daemon (code that runs periodically)


def main(args):
    '''This function contains interactive program code'''
    # Debug info
    print("directory: " + args.directory, "daemon: " +
          str(args.daemon), "remove: " + str(args.remove), sep='\n')
    # TODO: implement functionality
    create_database(args)


# ------------------------------------------------------------------------------
# Entry Point

if __name__ == "__main__":
    args = get_arguments()

    if args.daemon:
        log = open(os.getcwd() + '/daemon.log', 'w')
        with daemon.DaemonContext(
            stdout=log,
            stderr=log
        ):
            while True:
                main_daemon(args)
                time.sleep(DAEMON_SLEEP_TIME)
    else:
        main(args)
