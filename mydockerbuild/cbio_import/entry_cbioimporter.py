#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Commande pour lancer le conteneur cbioimporter:
# docker run -it --rm -v ~/Code/mydockerbuild/cbio_import/cbioimporter_vol/:/root/cbioimporter_vol cbioimporter

import os
import sys
import subprocess
import shlex
import argparse


if __name__ == '__main__':

    # On n'aura pas forcement besoin d'argument en entrée de script
    parser = argparse.ArgumentParser()

    # make study list
    volume = os.listdir(os.path.join(os.path.expanduser('~'), 'cbioimporter_vol', 'studies'))
    studies = [subdir for subdir in volume if os.path.isdir(os.path.join(os.path.expanduser('~'), 'cbioimporter_vol', 'studies', subdir))]

    for study in studies:
        # Avec ce nomage le rapport précendent est écrasé
        report = os.path.join(os.path.expanduser('~'), 'cbioimporter_vol', 'reports', 'myReport{}.html'.format(study))

        commande = './metaImport.py -s {} -o -u http://176.31.103.20:8888/cbioportal -v -html {}'.format(os.path.join(os.path.expanduser('~'), 'cbioimporter_vol', 'studies', study), report)

        print(study)
        print('Commande: {}'.format(commande))
        args = shlex.split(commande)
        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True, shell=False)
        stdout, stderr = process.communicate()
        print(stderr)
        print(stdout)
