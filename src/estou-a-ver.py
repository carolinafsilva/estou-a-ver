# ------------------------------------------------------------------------------
# Libraries

import subprocess
import argparse
import getpass
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


def PBKDF2(password):
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


def decrypt_AES_128_CBC(filename, salt, key, iv):
    '''This function decrypts with AES-128-CBC'''
    output = subprocess.run(
        ['openssl', 'enc', '-aes-128-cbc', '-d', '-K',
            key, '-in', filename, '-iv', iv, '-S', salt],
        stdout=subprocess.PIPE)
    return output

def decrypt_RSA(filename, key):
    '''This function decrypts with RSA'''
    output = subprocess.run(
        ['openssl', 'rsautl', '-decrypt', '-in',
            filename, '-inkey', key],
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


def create_database(args, password):
    '''This function creates an encrypted database of file hashes'''
    # Access global variable
    global DATABASE_INFO
    # Go to directory
    os.chdir(args.directory)
    # Database data
    hashes = create_hash_list(args.directory)
    data = '\n'.join(hashes)
    # Get encryption info
    output = PBKDF2(password)
    # Parse output
    output = output.stdout.split('\n')
    salt, key, iv = (output[0].split('=')[1],
                     output[1].split('=')[1],
                     output[2].split('=')[1])
    # Store info
    DATABASE_INFO = salt, key, iv
    # Encrypt the data
    encrypt_AES_128_CBC(DATABASE_NAME, data, salt, key, iv)


def read_database(args):
    '''This function returns a list of hashes read from the encrypted database'''
    # Go to directory
    os.chdir(args.directory)
    # Get info
    salt, key, iv = DATABASE_INFO
    # Decrypt the data
    output = decrypt_AES_128_CBC(DATABASE_NAME, salt, key, iv)
    # Return output
    return output.stdout.decode('utf-8').split('\n')


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
    password = getpass.getpass()
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
