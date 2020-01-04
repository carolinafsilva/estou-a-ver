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

DATABASE_INFO = None

# ------------------------------------------------------------------------------
# Data Structures


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
    output = subprocess.run(
        ['openssl', 'dgst', '-sha256', filename],
        stdout=subprocess.PIPE,
        universal_newlines=True)
    return output


def get_salt_key_iv(password):
    '''This function generates a salt, key, iv pair'''
    output = subprocess.run(
        ['openssl', 'enc', '-aes-256-cbc', '-k', password, '-P'],
        stdout=subprocess.PIPE,
        universal_newlines=True)
    return output


def encrypt_AES_128_CBC(filename, content, salt, key, iv):
    '''This function encrypts with AES-128-CBC'''
    output = subprocess.run(
        ['openssl', 'enc', '-aes-128-cbc', '-K',
            key, '-out', filename, '-iv', iv, '-S', salt],
        input=content,
        stdout=subprocess.PIPE,
        universal_newlines=True)
    return output


def decrypt_AES_128_CBC(filename):
    '''This function decrypts with AES-128-CBC'''
    salt, key, iv = DATABASE_INFO
    output = subprocess.run(
        ['openssl', 'enc', '-aes-128-cbc', '-d', '-K',
            key, '-in', filename, '-iv', iv, '-S', salt],
        stdout=subprocess.PIPE)
    return output


def create_database(args, password):
    '''This function calculates hashes SHA256 for all files inside a directory and saves them to the database'''
    # Access global variable
    global DATABASE_INFO
    # Go to directory
    os.chdir(args.directory)
    # Database data
    hashes = ''
    # For each file in directory
    for filename in get_files(args.directory):
        # Get hash
        output = SHA256(filename)
        # Add to list
        hashes += output.stdout
    # Get encryption info
    output = get_salt_key_iv(password)
    # Parse output
    output = output.stdout.split('\n')
    salt = output[0].split('=')[1]
    key = output[1].split('=')[1]
    iv = output[2].split('=')[1]
    # Store info
    DATABASE_INFO = salt, key, iv
    # Encrypt the data
    output = encrypt_AES_128_CBC(DATABASE_NAME, hashes, salt, key, iv)


def read_database(args):
    # Go to directory
    os.chdir(args.directory)
    # Decrypt the data
    output = decrypt_AES_128_CBC(DATABASE_NAME)
    return output.stdout.decode('utf-8')


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
    password = input("Insert a password for database: ")
    create_database(args, password)
    db = read_database(args)
    print(db)


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
