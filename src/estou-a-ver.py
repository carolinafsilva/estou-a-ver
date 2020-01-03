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


# guardar lista de ficheiros na observação anterior
holder = dict([(f, None) for f in os.listdir(args.directory)])


def directoryMonitor(holder):       # Verificar se existe alterações dentro da diretoria
    # guardar lista de ficheiros na observação atual
    current = dict([(f, None) for f in os.listdir(args.directory)])
    # Ver se algum ficheiro foi adicionado
    adicionado = [f for f in current if not f in holder]
    # Ver se algum ficheiro foi removido
    removido = [f for f in holder if not f in current]
    if adicionado:
        print("Adicionado: ", ", ".join(adicionado))
    if removido:
        print("Removido: ", ", ".join(removido))
    holder = current
    sha256Getter()


def main_daemon(args):
    '''This function contains daemon program code'''
    # TODO: implement daemon (code that runs periodically)
    print("directory: " + args.directory, "daemon: " +
          str(args.daemon), "remove: " + str(args.remove), sep='\n')

    directoryMonitor(holder)


def main(args):
    '''This function contains interactive program code'''
    # TODO: implement functionality
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
            while True:
                main_daemon(args)
                time.sleep(DAEMON_SLEEP_TIME)
    else:
        main(args)
