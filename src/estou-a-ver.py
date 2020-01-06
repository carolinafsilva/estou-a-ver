# ------------------------------------------------------------------------------
# Libraries

from tkinter import messagebox

import subprocess
import platform
import argparse
import tkinter
import getpass
import daemon
import shutil
import time
import sys
import os

# ------------------------------------------------------------------------------
# Global Variables

PLATFORM = platform.system()

DAEMON_SLEEP_TIME = 10

DATABASE_TUPLE = None

SALT = None

# ------------------------------------------------------------------------------
# Strings

DATABASE_NAME = '.database.aes'
DATABASE_BACKUP = '.database_backup.aes'

SKPK_NAME_AES = '.skpk.pem.aes'
SKPK_NAME = '.skpk.pem'
PK_NAME = '.pk.pem'

SALT_NAME = '.salt'

PROGRAM_DESCRIPTION = 'Directory management command-line utility'

DIRECTORY_HELP = 'Specifies which directory to operate on (default=cwd)'
DAEMON_HELP = 'Starts management as a daemon process'
REMOVE_HELP = 'Removes management from the specified directory'

MESSAGE_TITLE = 'Estou a Ver'

# ------------------------------------------------------------------------------
# Function Definitions


def get_files(directory):
    '''This function returns a list of files from the directory'''
    return [f for f in os.listdir(directory) if not f[0] == '.' and os.path.isfile(f)]


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
        stderr=subprocess.DEVNULL,
        universal_newlines=True)
    return output


def PBKDF2(salt, password):
    '''This function returns key, iv tuple'''
    if salt == None:
        # Libressl
        if PLATFORM == 'Darwin':
            output = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc', '-k', password, '-P'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                universal_newlines=True)
        # Openssl
        elif PLATFORM == 'Linux':
            output = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc',
                    '-k', password, '-P', '-pbkdf2'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                universal_newlines=True)
    else:
        # Libressl
        if PLATFORM == 'Darwin':
            output = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc',
                    '-k', password, '-P', '-S', salt],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                universal_newlines=True)
        # Openssl
        elif PLATFORM == 'Linux':
            output = subprocess.run(
                ['openssl', 'enc', '-aes-128-cbc',
                    '-k', password, '-P', '-S', salt, '-pbkdf2'],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                universal_newlines=True)
    # Parse output
    output = output.stdout.rstrip().split('\n')
    salt = output[0].split('=')[1]
    key, iv = (output[1].split('=')[1],
               output[2].split('=')[1])
    # Save SALT
    global SALT
    SALT = salt
    # Update .salt file
    with open(SALT_NAME, 'w') as f:
        f.write(salt)
    # Return tuple
    return key, iv


def encrypt_AES_128_CBC(filename, content, key, iv):
    '''This function encrypts with AES-128-CBC'''
    output = subprocess.run(
        ['openssl', 'enc', '-aes-128-cbc', '-K',
            key, '-out', filename, '-iv', iv],
        input=content,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True)
    return output


def encrypt_AES_128_CBC_bytes(filename, content, key, iv):
    '''This function encrypts with AES-128-CBC'''
    output = subprocess.run(
        ['openssl', 'enc', '-aes-128-cbc', '-K',
            key, '-out', filename, '-iv', iv],
        input=content,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)
    return output


def decrypt_AES_128_CBC(filename, key, iv):
    '''This function decrypts with AES-128-CBC'''
    output = subprocess.run(
        ['openssl', 'enc', '-aes-128-cbc', '-d', '-K',
            key, '-in', filename, '-iv', iv],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)
    return output


def decrypt_AES_128_CBC_to_file(fin, fout, key, iv):
    '''This function decrypts with AES-128-CBC'''
    output = subprocess.run(
        ['openssl', 'enc', '-aes-128-cbc', '-d', '-K',
            key, '-in', fin, '-out', fout, '-iv', iv],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)
    return output


def generate_RSA(filename, size):
    '''This function generates a RSA key pair'''
    output = subprocess.run(
        ['openssl', 'genrsa', '-out', filename, size],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True)
    return output


def extract_pk_RSA(filename, key_pair):
    '''This function extracts a public key from a RSA key pair'''
    output = subprocess.run(
        ['openssl', 'rsa', '-in', key_pair, '-out', filename, '-pubout'],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        universal_newlines=True)
    return output


def sign_RSA(sk, h):
    '''This function signs with RSA'''
    output = subprocess.run(
        ['openssl', 'rsautl', '-sign', '-inkey', sk],
        input=h.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)
    return output


def decrypt_signature_RSA(rsa_cipher, pk):
    '''This function decrypts the digital signature'''
    output = subprocess.run(
        ['openssl', 'rsautl', '-verify', '-inkey', pk, '-pubin'],
        input=rsa_cipher,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)
    return output


def verify_RSA(filename, rsa_cipher, pk):
    '''This function verifies signatures'''
    sha = SHA256(filename).stdout.rstrip()
    sig = decrypt_signature_RSA(rsa_cipher, pk).stdout.decode('utf-8').rstrip()
    return sha == sig


def create_hash_list(directory):
    '''This function returns a list of filename, hash tuples'''
    hashes = []
    # For each file in directory
    for filename in get_files(directory):
        # Get hash
        output = SHA256(filename)
        output = output.stdout.rstrip()
        # Add to list
        hashes.append((filename, output))
    return hashes


def create_signature_list(hashes):
    '''This function returns a list of signatures'''
    # Get tuple
    key, iv = DATABASE_TUPLE
    # Decrypt sk
    decrypt_AES_128_CBC_to_file(SKPK_NAME_AES, SKPK_NAME, key, iv)
    # Create list
    signed = []
    for filename, h in hashes:
        output = sign_RSA(SKPK_NAME, h)
        signature = output.stdout
        signed.append((filename, signature))
    # Encrypt sk
    with open(SKPK_NAME, 'r') as f:
        content = f.read()
        encrypt_AES_128_CBC(SKPK_NAME_AES, content, key, iv)
    return signed


def create_database(directory, password):
    '''This function creates an encrypted database of signatures'''
    # Access global variables
    global DATABASE_TUPLE
    # Generate key, iv
    key, iv = PBKDF2(None, password)
    # Store tuple
    DATABASE_TUPLE = key, iv
    # Generate rsa
    generate_RSA(SKPK_NAME, '2048')
    # Extract public key
    extract_pk_RSA(PK_NAME, SKPK_NAME)
    # Encrypt sk
    with open(SKPK_NAME, 'r') as f:
        content = f.read()
        encrypt_AES_128_CBC(SKPK_NAME_AES, content, key, iv)
    # TODO: delete SKPK_NAME
    # Get hashes
    hashes = create_hash_list(directory)

    # Sign hashes
    signed = create_signature_list(hashes)
    # Join b string
    signatures = b''
    for d, s in signed:
        signatures += d.encode() + b'\x01\x01\x01\x01' + \
            s + b'\x00\x00\x00\x00'
    # Encrypt the database
    encrypt_AES_128_CBC_bytes(DATABASE_NAME, signatures, key, iv)


def read_database(directory):
    '''This function returns a list of hashes read from the encrypted database'''
    # Get tuple
    key, iv = DATABASE_TUPLE
    # Decrypt the data
    output = decrypt_AES_128_CBC(DATABASE_NAME, key, iv)
    # Return output
    try:
        output = output.stdout
        # Parse output
        output = output.split(b'\x00\x00\x00\x00')
        signed = []
        for b in output:
            signed.append(b.split(b'\x01\x01\x01\x01'))
        signed.pop()
    except:
        signed = 'ERROR'
    return signed


def monitor_directory(directory, db, is_daemon):
    '''This function verifies all signatures'''
    files = get_files(directory)
    changes = False
    first = True
    for f in files:
        found = False
        for filename, signature in db:
            filename = filename.decode('utf-8')
            if f == filename:
                found = True
                if not verify_RSA(f, signature, PK_NAME):
                    if is_daemon:
                        warn_user(f + ' was altered')
                    else:
                        print(f, 'was altered')
                    changes = True
            if filename not in files and first:
                if is_daemon:
                    warn_user(filename + ' was deleted')
                else:
                    print(filename, 'was deleted')
                changes = True
        first = False
        if not found:
            if is_daemon:
                warn_user(f + ' was added')
            else:
                print(f, 'was added')
            changes = True
    return changes


def warn_user(message):
    '''This function notifies the user'''
    # Hide main window
    root = tkinter.Tk()
    root.withdraw()
    # Display info
    messagebox.showinfo(MESSAGE_TITLE, message)


def monitor(is_daemon):
    # Read Database
    db = read_database(args.directory)
    if not db == 'ERROR':
        # Verify Signatures
        if not monitor_directory(args.directory, db, is_daemon):
            shutil.move('./' + DATABASE_NAME, './' + DATABASE_BACKUP)
            create_database(args.directory, password)
    else:
        if is_daemon:
            warn_user('Datavase integrity compromised')
        else:
            print('Database integrity compromised')
            if os.path.isfile(DATABASE_BACKUP):
                ans = input('Do you wish to recover the last backup? [Y/n] ')
                ans = ans.lower()
                if not ans == 'n':
                    shutil.move('./' + DATABASE_BACKUP, './' + DATABASE_NAME)


def main_daemon(args):
    '''This function contains daemon program code'''
    # Access
    global DATABASE_TUPLE
    # Generate key, iv
    DATABASE_TUPLE = PBKDF2(SALT, password)
    # Monitor
    monitor(True)


def main(args):
    '''This function contains interactive program code'''
    # Access
    global DATABASE_TUPLE
    # Generate key, iv
    DATABASE_TUPLE = PBKDF2(SALT, password)
    # Create Database
    if not os.path.isfile(DATABASE_NAME):
        create_database(args.directory, password)
        print('Directory is now being monitored')
    else:
        # Monitor
        monitor(False)


# ------------------------------------------------------------------------------
# Entry Point
if __name__ == "__main__":

    # Get arguments
    args = get_arguments()

    # If remove flag set
    if not args.remove:

        # Go to directory
        os.chdir(args.directory)

        # Read salt
        if os.path.isfile(SALT_NAME):
            f = open(SALT_NAME, 'r')
            SALT = f.read()

        # Read password
        password = getpass.getpass()

        # If daemon flag set
        if args.daemon:

            # Debug info
            log = open('.daemon.log', 'w')

            # Create Database
            if not os.path.isfile(DATABASE_NAME):
                create_database(args.directory, password)
                print('Directory is now being monitored')

            # Start daemon
            print('Started daemon')
            with daemon.DaemonContext(
                stdout=log,
                stderr=log
            ):
                while True:
                    main_daemon(args)
                    time.sleep(DAEMON_SLEEP_TIME)
        else:
            main(args)
    else:
        if os.path.exists('.daemon.log'):
            os.remove('.daemon.log')
        if os.path.exists(DATABASE_NAME):
            os.remove(DATABASE_NAME)
        if os.path.exists(DATABASE_BACKUP):
            os.remove(DATABASE_BACKUP)
        if os.path.exists(PK_NAME):
            os.remove(PK_NAME)
        if os.path.exists(SALT_NAME):
            os.remove(SALT_NAME)
        if os.path.exists(SKPK_NAME):
            os.remove(SKPK_NAME)
        if os.path.exists(SKPK_NAME_AES):
            os.remove(SKPK_NAME_AES)
