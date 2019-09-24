#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Commande pour lancer le conteneur vcf2maf:
# docker run -it --rm -v ~/Code/mydockerbuild/vcf2maf/VEP_volume/cache/.vep:/root/.vep -v ~/Code/mydockerbuild/vcf2maf/volume_data:/data vcf2maf --input-vcf /data/test.vcf --output-maf /data/test.maf

import os
import subprocess
import shlex
import argparse
import csv
import shutil


def vcf2maf_cmd(input_path, output_path, tumor_barcode=None):
    """ Build vcf2maf command. """

    vep_dir = os.path.expandvars("$VEP_DIR")

    cmd = 'perl vcf2maf.pl --vep-path {} --custom-enst /root/.vep/isoform_overrides_uniprot \
    --input-vcf {} --output-maf {} --ref-fasta \
    /root/.vep/homo_sapiens/91_GRCh37/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa.gz'

    if tumor_barcode:
        cmd = cmd + ' --tumor-id {}'.format(tumor_barcode)

    return cmd.format(vep_dir, shlex.quote(input_path), shlex.quote(output_path))


def call_perl(cmd):
    """Call perl script in vcf2maf container."""

    print('\x1b[1;34;40m call perl script \x1b[0m')

    args_process = shlex.split(cmd)
    process = subprocess.Popen(args_process, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True, shell=False)
    stdout, stderr = process.communicate()
    print(stderr)
    print(stdout)


def concatenate_maf_files(in_dir, out_file_path):
    """ Colle le contenu des fichiers sans dupliquer le header.

        La function doit marcher avec tout les csv contenant un header
    """
    liste_file_name = os.listdir(in_dir)
    # print('\x1b[1;33;39m Dans temp_maf_dir (normalement):\x1b[0m')
    # print(list_file_name)

    headers = []
    lines = []

    # lecture
    first_file = True
    for file_name in liste_file_name:
        flag_header = True
        """ 1er fichier on copie le header """
        if first_file:
            first_file = False
            with open(os.path.join(in_dir, file_name), 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for line in reader:
                    if line[0][0] == '#':
                        headers.append(line)
                    else:
                        if flag_header:
                            headers.append(line)
                            flag_header = False
                        else:
                            lines.append(line)
        else:
            with open(os.path.join(in_dir, file_name), 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                for line in reader:
                    if line[0][0] != '#':
                        if flag_header:
                            flag_header = False
                        else:
                            lines.append(line)

    with open(out_file_path, 'w') as f:
        w = csv.writer(f, delimiter='\t')
        for line in headers:
            w.writerow(line)
        for line in lines:
            w.writerow(line)


def map_tumor_barcode(map_file):

    map = {}

    with open(map_file) as f:
        dict_reader = csv.DictReader(f, delimiter='\t')

        for row in dict_reader:
            map[row['filename']] = row['tumor_barcode']

    return map


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--input-vcf', required=True)
    parser.add_argument('--output-maf')
    parser.add_argument('--merge-maf', action='store_true')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', action='store_true', help='Put this option if the input\
     is a directory of .vcf files')
    group.add_argument('--tumor-barcode', help='Value to put in Tumor_Sample_Barcode colomn')

    parser.add_argument('--tumor-barcode-map', help='csv file that map filenames with tumor-id, must be in \
        container volume')

    args = parser.parse_args()

    # Si on convertit tout un dossier
    if args.d:
        print('\x1b[1;34;40m Dans args.d \x1b[0m')
        if args.tumor_barcode_map:
            tumor_barcode_s = map_tumor_barcode(args.tumor_barcode_map)
        else:
            # On donne par défault un tumor_barcode à chaque fichier
            pass

        list_file_name = os.listdir(args.input_vcf)

        # Significations de out_maf_folder:
        #   Si l'option --merge-maf est choisi out_maf_folder ne désigne que le chemin
        #   du dossier intermediaire entre la convertion vcf2maf et la fusion des .maf
        #   Si --merge-maf n'est pas choisi out_maf_folder désigne le chemin du dossier
        #   contenant les fichiers .maf une fois l'application terminée
        if args.merge_maf:
            print('\x1b[1;34;40m Dans args.merge_maf \x1b[0m')
            if not os.path.exists(os.path.join(os.sep, 'data', 'temp_maf_dir')):
                os.mkdir(os.path.join(os.sep, 'data', 'temp_maf_dir'))
                os.chmod(os.path.join(os.sep, 'data', 'temp_maf_dir'), 0o777)
            out_maf_folder = os.path.join(os.sep, 'data', 'temp_maf_dir')
        else:
            if args.output_maf is None:
                if not os.path.exists(os.path.join(os.sep, 'data', 'default_output_maf_dir')):
                    os.mkdir(os.path.join(os.sep, 'data', 'default_output_maf_dir'))
                    os.chmod(os.path.join(os.sep, 'data', 'default_output_maf_dir'), 0o777)
                out_maf_folder = os.path.join(os.sep, 'data', 'default_output_maf_dir')
            else:
                if not os.path.exists(args.output_maf):
                    os.mkdir(args.output_maf)
                    os.chmod(args.output_maf, 0o777)
                out_maf_folder = args.output_maf
    else:
        # print('\x1b[1;34;40m Else args.d \x1b[0m')
        list_file_name = [args.input_vcf]
        out_maf_folder = os.path.join(os.sep, 'data')

    # Fichier (.vcf) par fichier
    for file_name in list_file_name:
        # print('\x1b[1;34;40m {} \x1b[0m'.format(file_name))

        input_path = os.path.join(args.input_vcf, file_name)
        fname_no_ext = os.path.splitext(file_name)[0]  # On ne garde pas le .vcf pour le nom de fichier de sortie

        if args.output_maf is None:
            vcf2maf_outfile = os.path.join(out_maf_folder, fname_no_ext) + ".maf"
        else:
            vcf2maf_outfile = os.path.join(out_maf_folder, fname_no_ext) + ".maf"

        try:
            tumor_barcode = tumor_barcode_s[file_name]
        except KeyError:
            # On donne une valeur par default si le mapping ne donne aucun tumor_barcode correspondant
            # au nom de fichier .vcf
            print('Warning: {}\'s Tumor_Sample_Barcode column has been given \
            a default value.'.format(file_name))
            tumor_barcode = fname_no_ext
        # Si il n'y a pas de fichier de mapping
        except NameError:
            if (args.tumor_barcode):
                tumor_barcode = args.tumor_barcode
            else:
                # print('\x1b[1;33m Warning: {}\'s Tumor_Sample_Barcode column has been given \
                # a default value \x1b[0m'.format(file_name))
                tumor_barcode = fname_no_ext

        # La commande perl ne semble pas lire correctement les espaces même en utilisant shlex.quote()
        # au préalable.
        if ' ' in input_path:
            print('Notice: {} contient un espace; renomage du fichier temporaire: \' \' -> _'.format(input_path))
            vcf2maf_outfile_no_space = vcf2maf_outfile.replace(' ', '_')
            input_path_no_space = input_path.replace(' ', '_')
            os.rename(input_path, input_path_no_space)
        else:
            vcf2maf_outfile_no_space = vcf2maf_outfile
            input_path_no_space = input_path

        cmd = vcf2maf_cmd(input_path_no_space, vcf2maf_outfile_no_space, tumor_barcode)
        call_perl(cmd)

        # vcf2maf's in path without file extension
        no_ext = os.path.splitext(input_path_no_space)[0]
        try:
            os.remove(no_ext + ".vep.vcf")
        except FileNotFoundError as e:
            print('Notice: {} est vide'.format(file_name))

    if args.merge_maf:
        concatenate_maf_files(out_maf_folder, args.output_maf)

    # Suppression dossier temporaire des fichiers maf
    if args.d and args.merge_maf:
        shutil.rmtree(out_maf_folder)
