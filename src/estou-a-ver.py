# ------------------------------------------------------------------------------
# Libraries

import subprocess
import platform
import argparse
import getpass
import daemon
import time
import sys
import os

# ------------------------------------------------------------------------------
# Global Variables

PLATFORM = platform.system()

DATABASE_NAME = "database.aes"

DATABASE_TRIPLE = None

DAEMON_SLEEP_TIME = 300

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


def PBKDF2(salt, password):
    '''This function returns salt, key, iv triplet'''
    if salt == None:
        # Libressl
        if PLATFORM == 'Darwin':
            output = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc', '-k', password, '-P'],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            return output
        # Openssl
        elif PLATFORM == 'Linux':
            output = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc',
                    '-k', password, '-P', '-pbkdf2'],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            return output
    else:
        # Libressl
        if PLATFORM == 'Darwin':
            output = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc',
                    '-k', password, '-P', '-S', salt],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            return output
        # Openssl
        elif PLATFORM == 'Linux':
            output = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc',
                    '-k', password, '-P', '-S', salt, '-pbkdf2'],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            return output


def encrypt_AES_128_CBC(filename, content, key, iv):
    '''This function encrypts with AES-128-CBC'''
    output = subprocess.run(
        ['openssl', 'enc', '-aes-128-cbc', '-K',
            key, '-out', filename, '-iv', iv],
        input=content,
        stdout=subprocess.PIPE,
        universal_newlines=True)
    return output


def decrypt_AES_128_CBC(filename, key, iv):
    '''This function decrypts with AES-128-CBC'''
    output = subprocess.run(
        ['openssl', 'enc', '-aes-128-cbc', '-d', '-K',
            key, '-in', filename, '-iv', iv],
        stdout=subprocess.PIPE)
    return output


def create_hash_list(directory):
    '''This function returns a list of hashes'''
    hashes = ''
    # For each file in directory
    for filename in get_files(directory):
        # Get hash
        output = SHA256(filename)
        # Add to list
        hashes += output.stdout
    # Format data
    return hashes.rstrip().split('\n')


def create_database(directory, password):
    '''This function creates an encrypted database of file hashes'''
    # Access global variable
    global DATABASE_TRIPLE
    # Generate salt, key, iv
    output = PBKDF2(None, password)
    # Parse output
    output = output.stdout.rstrip().split('\n')
    salt, key, iv = (output[0].split('=')[1],
                     output[1].split('=')[1],
                     output[2].split('=')[1])
    # Store triple
    DATABASE_TRIPLE = salt, key, iv
    # Go to directory
    os.chdir(directory)
    # Database data
    hashes = create_hash_list(directory)
    # TODO: Sign hashes
    data = '\n'.join(hashes)
    # Encrypt the data
    encrypt_AES_128_CBC(DATABASE_NAME, data, key, iv)


def read_database(directory):
    '''This function returns a list of hashes read from the encrypted database'''
    # Get triple
    salt, key, iv = DATABASE_TRIPLE
    # Go to directory
    os.chdir(directory)
    # Decrypt the data
    output = decrypt_AES_128_CBC(DATABASE_NAME, key, iv)
    # Return output
    return output.stdout.decode('utf-8').split('\n')


def main_daemon(args):
    '''This function contains daemon program code'''
    # TODO: implement daemon (code that runs periodically)


def main(args):
    '''This function contains interactive program code'''
    # Read password
    password = getpass.getpass()
    # Create Database
    create_database(args.directory, password)
    # Read Database
    db = read_database(args.directory)
    # Debug info
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
