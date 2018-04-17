#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import shlex
import subprocess
import os.path as path
import argparse


""" Transfer all reports from k2so master node and virtual node. """


def args():
    """Parse options."""
    opt_parser = argparse.ArgumentParser(description=__doc__)
    opt_parser.add_argument('--reports-path', required=True, help='Local path for cbioportal reports')
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

    study_path_masternode = '/scratch/pmancini/cbioportal'
    study_path_virtualnode = '/data/dockerbuilds/cbioportal/studies/'

    reports_remote_path = '/scratch/pmancini/cbioportal/reports'

    args = args()

    reports_local_path = args.reports_path

    # Les reports sont les fichiers .html, donc on vide cbio_studies/ de tout ses fichiers
    # .html

    # Dev: La commande utilisé pour l'importation
    importation = './cbioportal/core/src/main/scripts/importer/metaImport.py -s '
    '/cbio_studies/lung_study_listes/ -o -u http://localhost:8080/cbioportal -v -html'
    ' /cbio_studies/myReportlunglistes.html'

    # Working directory = dossier reports
    local_wd = path.join(*path.normpath(reports_local_path).split('/')[:-1])

    # /scratch est monté sur tout les noeuds => transfert virtual node -> master node inutile

    # transfert master node /scratch -> local
    # Aucun report ne reste sur le scratch
    local_cmd_list = ['rsync -av --include=\'*.html\' --remove-source-files {}:{}/ {}'.format(k2so_login,
        reports_remote_path, 'reports')]


    local_cmd = ''
    for cmd in local_cmd_list:
        local_cmd = local_cmd + '\n' + cmd
    subprocess.run(local_cmd, shell=True, cwd=local_wd)
