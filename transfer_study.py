#!/usr/bin/env python3
# -*- coding: utf-8 -*-


""" Transfer study to cBioportal instance. """


import argparse
import sys
import shlex
import subprocess
import yaml
import os.path as path
from bcolors import Bcolors
import time


def args():
    """Parse options."""
    opt_parser = argparse.ArgumentParser(description=__doc__)
    opt_parser.add_argument('--study-path', required=True)
    return opt_parser.parse_args()


def ssh_k2so(cmd_list, login, cwd=None):
    """Call subprocess on remote server through ssh.

        :return: stdout and stderr of subprocess.
    """

    remote_cmd = ''
    for cmd in cmd_list:
        remote_cmd = remote_cmd + '\n' + cmd

    sshProcess = subprocess.Popen(['ssh', '-T', k2so_login],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True,
                               bufsize=0,
                               cwd=cwd)

    return sshProcess.communicate(remote_cmd)



if __name__ == '__main__':

    k2so_login = 'root@129.10.28.20'

    cbio_image_name = 'cbioportal'

    args = args()

    study_name = path.basename(path.normpath(args.study_path))
    study_path_masternode = '/scratch/pmancini/cbioportal'
    study_path_virtualnode = '/data/dockerbuilds/cbioportal/studies/'

    local_wd = path.join(*path.normpath(args.study_path).split('/')[:-1])

    # Copie du dossier study sur k2so
    print('Transfert du dossier {} sur {}'.format(Bcolors.OKBLUE + study_name + Bcolors.ENDC,
        Bcolors.OKBLUE + k2so_login + Bcolors.ENDC))
    # Backup des study localement
    local_cmd_list = ['scp -r {} {}:{}'.format(study_name, k2so_login, path.join(study_path_masternode, study_name)),
        'mv -f {name} studies_backup/{name}{time}'.format(name=study_name,
            time=time.strftime('-%H:%M-%d-%m', time.localtime()))
    ]

    local_cmd = ''
    for cmd in local_cmd_list:
        local_cmd = local_cmd + '\n' + cmd

    subprocess.run(local_cmd, shell=True, cwd=local_wd)

    # Backup de la précédente study si elle a le même nom
    bash_cmd = 'cd {virtual} \n mv -f {name} studies_backup/{name}{time}'.format(name=study_name,
            time=time.strftime('-%H:%M-%d-%m', time.localtime()), virtual=study_path_virtualnode)
    remote_cmd_list = ['ssh kvm01 -t \'bash -c -l "{}"\' '.format(bash_cmd)]

    outs, errs = ssh_k2so(remote_cmd_list, k2so_login)

    if errs[:2] == 'mv':
        print('Virtual node already clean')
    elif errs:
        print(outs)
        print('Error virtual node:')
        print(errs)
    else:
        print(outs)

    # Copie depuis le noeud maitre vers le noeud de virtualisation
    cmd = ['cd {}'.format(study_path_masternode),
        'scp -r {name} root@kvm01:{virtual}{name}'.format(name=study_name, virtual=study_path_virtualnode)
    ]

    outs, errs = ssh_k2so(cmd, k2so_login)

    if errs:
        print(outs)
        print('Error copy from master node:')
        print(errs)
    else:
        print(outs)

    # Suppression de l'ancienne study sur k2so noeud maitre
    print('Nétoyage du noeud maitre: rm dossier {} sur {}'.format(Bcolors.OKBLUE + study_name + Bcolors.ENDC,
        Bcolors.OKBLUE + k2so_login + ':' + study_path_masternode + Bcolors.ENDC))

    # Rien sur le noeud maitre
    remote_cmd_list = ['cd {}'.format(study_path_masternode),
        'rm -fr {}'.format(study_name)
    ]

    outs, errs = ssh_k2so(remote_cmd_list, k2so_login)

    # Ignore l'erreur si la study n'est pas déjà présente
    if errs:
        print(outs)
        print('Remote error:')
        print(errs)
    else:
        print(outs)
