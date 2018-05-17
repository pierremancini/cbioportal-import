#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, csv, re, shutil
import argparse
import subprocess
import shlex
import yaml
import time

# DEV
import IPython.core.ultratb
from pprint import pprint
# sys.excepthook = IPython.core.ultratb.ColorTB()


""" Ce script créé les metadata et data à insérer dans cbioportal

    Exemple d'utilisation:

    python build_study_data.py --in-dir in_build_study --out-dir dev_test

"""


def extract_anapath(file_name):
    """ Extract anapath n° a.k.a sample_id from a file name.
    """
    iter_anapath = re.finditer(r"(?:[ \-_]{1})([A-Za-z]{1,2}[0-9]{1,3}).*", file_name)
    for match_anapath in iter_anapath:
        if match_anapath is not None:
            return match_anapath.group(1)


def get_studies_samples(studies):
    """ Create list of samples to select.
    """

    list_selected_anapath = []

    for study_file in studies:
        with open(study_file, 'rb') as f:
            for line in f:
                anapath = line.replace("\n", '')
                match_iter = re.finditer(r"-F$", anapath)
                for match in match_iter:
                    if match is not None:
                        anapath = anapath.replace("-F", "")
                list_selected_anapath.append(anapath)

    return list_selected_anapath


def select_samples(dir, studies, out_dir):
    """ Sélectionne les échantillons présents dans les fichiers de la liste studies.

        Les fichiers correspondant aux échantillons sélectionnés sont copiés dans
        un dossier selected_samples.

        Retourne [0] -> chemin vers le dossier des fichiers copiés
                 [1] -> liste des numéro anapath selectionnés
    """

    # On supprime le dossier selected_samples précédent
    selected_samples_path = os.path.join(out_dir, 'selected_samples')
    if os.path.exists(selected_samples_path):
        shutil.rmtree(selected_samples_path)
    os.mkdir(selected_samples_path)

    list_selected_anapath = []

    # Création la liste des échantillons à sélectionner
    list_selected_anapath = get_studies_samples(studies)

    file_list = os.listdir(dir)

    if not os.path.exists(os.path.join(out_dir, 'no-study')):
        os.mkdir(os.path.join(out_dir, 'no-study'))
    else:
        shutil.rmtree(os.path.join(out_dir, 'no-study'))
        os.mkdir(os.path.join(out_dir, 'no-study'))

    tumor_map = {}

    for file_name in file_list:
        # On extrait le n° anapath de chaque fichier
        sample_id = extract_anapath(file_name)

        if sample_id in list_selected_anapath:
            # tumor barcode mapping
            tumor_map[file_name] = sample_id
            shutil.copyfile(os.path.join(dir, file_name), os.path.join(selected_samples_path, file_name))
        else:
            shutil.copyfile(os.path.join(dir, file_name), os.path.join(out_dir, 'no-study', file_name))

    return (selected_samples_path, list_selected_anapath, tumor_map)


def make_dict_samples(selected_anapath):
    """Ecrit le dictionnaire qui classe les sampled_id par patient_id."""

    dict_samples = {}

    with open(os.path.join(in_dir, config['anapath_patient'])) as f:

        # Dans le fichier de configuration de correspondance 'anapath_patient', la 1er colonne 
        # correspond aux n° anapath/sample_id, la 2em colonne correspond aux patient_id


        reader = csv.reader(f, delimiter=',')
        for line in reader:
            line[0] = line[0].translate(None, ' ')
            # {patient_id: [sample_id]}
            patient_id = line[1]
            sample_id = line[0]

            # On ne met que les échantillons préalablement sélectionnés
            if sample_id in selected_anapath:
                dict_samples.setdefault(patient_id, []).append(sample_id)

    return dict_samples


def use_vcf2maf(in_dir, out_dir, vcf_folder_path, tumor_map):
    """ Use vcf2maf container directory given as argument. """

    vcf_folder_name = os.path.basename(vcf_folder_path)

    volume_path = os.path.join(os.path.expanduser('~'), 'Code', 'mydockerbuild', 'vcf2maf', 'volume_data')

    # On déplace le fichier dans le volume du container
    # - override
    if os.path.exists(os.path.join(volume_path, vcf_folder_name)):
        shutil.rmtree(os.path.join(volume_path, vcf_folder_name))

    shutil.copytree(os.path.join(in_dir, vcf_folder_name),
        os.path.join(volume_path, vcf_folder_name))

    # Transmission du mapping des TUMOR_BARCODE par fichier .csv
    with open(os.path.join(volume_path, 'tumor_barcode_map.tsv'), 'w') as csvfile:
        header = ['filename', 'tumor_barcode']
        writer = csv.DictWriter(csvfile, fieldnames=header, delimiter='\t')
        writer.writeheader()
        for filename in tumor_map:
            writer.writerow({'filename': filename, 'tumor_barcode': tumor_map[filename]})

    # Il sagit des path une fois dans le conteneur
    map_path = os.path.join(os.sep, 'data', 'tumor_barcode_map.tsv')
    vcf_path = os.path.join(os.sep, 'data', vcf_folder_name)
    maf_path = os.path.join(os.sep, 'data', 'mutations.maf')
    vep_vol = os.path.expanduser('~') + '/Code/mydockerbuild/vcf2maf/VEP_volume/cache/.vep:/root/.vep'

    # Création de fichier d'annotation à partir des fichiers .vcf du dossier trio
    # Le dossier 'temp_maf_dir', ressemblant les .maf avant merge, est créé dans le volume du conteneur
    vcf2maf_vol = volume_path + ':/data'

    cmd = "docker run -it --rm -v {} -v {} vcf2maf --input-vcf {} --output-maf {}" \
          " --tumor-barcode-map {} -d --merge-maf".format(vep_vol,
                                                         vcf2maf_vol,
                                                         vcf_path,
                                                         maf_path,
                                                         map_path)
    args = shlex.split(cmd)
    subprocess.call(args)

    # Ramène le fichier de mutations dans le dossier de destiantion de la fonction
    shutil.copy(os.path.join(volume_path, 'mutations.maf'), out_dir)


def write_meta_files(to_import_dir, config):

    with open(os.path.join(to_import_dir, 'meta_study.txt'), 'wb') as f:
        f.write('type_of_cancer: {}\n'.format(config['meta_study']['type_of_cancer']))
        f.write('cancer_study_identifier: {}\n'.format(config['cancer_study_identifier']))
        name = config['meta_study']['name']
        if name:
            name = config['meta_study']['name']
        else:
            f.write('name: {}\n'.format(os.path.basename(to_import_dir)))
        f.write('description: {}\n'.format(config['meta_study']['description']))
        f.write('short_name: {}\n'.format(config['meta_study']['short_name']))
        f.write('add_global_case_list: {}\n'.format(config['meta_study']['add_global_case_list']))

    # meta clinical
    with open(os.path.join(to_import_dir, 'meta_samples.txt'), 'wb') as f:
        f.write('cancer_study_identifier: {}\n'.format(config['cancer_study_identifier']))
        f.write('genetic_alteration_type: {}\n'.format(config['meta_samples']['genetic_alteration_type']))
        f.write('datatype: {}\n'.format(config['meta_samples']['datatype']))
        f.write('data_filename: {}\n'.format(config['meta_samples']['data_filename']))

    with open(os.path.join(to_import_dir, 'meta_patients.txt'), 'wb') as f:
        f.write('cancer_study_identifier: {}\n'.format(config['cancer_study_identifier']))
        f.write('genetic_alteration_type: {}\n'.format(config['meta_patients']['genetic_alteration_type']))
        f.write('datatype: {}\n'.format(config['meta_patients']['datatype']))
        f.write('data_filename: {}\n'.format(config['meta_patients']['data_filename']))

    with open(os.path.join(to_import_dir, 'meta_mutations_extended.txt'), 'wb') as f:
        f.write('cancer_study_identifier: {}\n'.format(config['cancer_study_identifier']))
        f.write('genetic_alteration_type: {}\n'.format(config['meta_mutations_extended']['genetic_alteration_type']))
        f.write('datatype: {}\n'.format(config['meta_mutations_extended']['datatype']))
        f.write('stable_id: {}\n'.format(config['meta_mutations_extended']['stable_id']))
        f.write('show_profile_in_analysis_tab: {}\n'.format(config['meta_mutations_extended']['show_profile_in_analysis_tab']))
        f.write('profile_name: {}\n'.format(config['meta_mutations_extended']['profile_name']))
        f.write('profile_description: {}\n'.format(config['meta_mutations_extended']['profile_description']))
        f.write('data_filename: {}\n'.format(config['meta_mutations_extended']['data_filename']))
        f.write('swissprot_identifier: {}\n'.format(config['meta_mutations_extended']['swissprot_identifier']))


if __name__ == '__main__':
    """ Dossier à traiter, donné en 1er argument du script

        Ce dossier doit contenir:
        -  anapathpatient20161206092905.csv.csv (n° anapath  / n° patient )
        -  NGS colon-lung échantillons COLONS_anapath.txt (n° anapath / colon)
        -  NGS colon-lung échantillons POUMONS_anapath.txt (n° anapath / lung)
        -  Le dossier de sortie du script filter_trio.py "new_vcf" que l'on renomera vcf
    """
    parser = argparse.ArgumentParser()

    # Le dossier donné par --in-dir doit contenir:
    #   - le fichier de mapping n° anapath  / n° patient
    #   - les fichiers listant les n° anapath de la study
    #   - Un dossier contenant les .vcf, le nom de ce dossier est donné dans build_config.yml
    parser.add_argument('--in-dir', help='Directory containing: vcf directory, mapping files')
    parser.add_argument('--out-dir')
    parser.add_argument("--report", action='store_true',
     help="Get a HTML report cbioportal validation in curent directory")
    parser.add_argument("-c", "--config", help="Specify path to config file")
    parser.add_argument('--mv', action='store_true')
    args = parser.parse_args()

    in_dir = args.in_dir  # ex: in_build_study

    if args.config:
        with open(args.config, 'r') as ymlfile:
            config = yaml.load(ymlfile)
    else:
        default_file = "build_config.yml"
        with open(default_file, 'r') as ymlfile:
            config = yaml.load(ymlfile)
            print("Notice: {} est utilisé comme fichier de configuration".format(default_file))

    # Gestion des conflits de nom avec un potentiel ancien dossier de sortie du script
    if os.path.exists(args.out_dir):
        backup_path = '{}-{}'.format(args.out_dir, time.time())
        if args.mv:
            print('Moving {} to {}'.format(args.out_dir, backup_path))
            shutil.move(args.out_dir, backup_path)
        else:
            print('Must remove the previous folder named {} before creating new one.'.format(args.out_dir))
            move = raw_input('Move {} to {} ? (y/n) '.format(args.out_dir, backup_path))
            if move == 'y':
                shutil.move(args.out_dir, backup_path)
            else:
                sys.exit('exit {}'.format(__file__))

    # Creation du nouveau dossier de sortie
    print('Create new folder {}'.format(args.out_dir))
    os.mkdir(args.out_dir)

    # cancer_study_indentifier donne son nom au dossier d'importation dans cBioportal
    to_import_dir = os.path.join(args.out_dir, config['cancer_study_identifier'])

    case_list_ids = []
    concat_ok = {}

    vcf_path = os.path.join(in_dir, config['vcf_folder_name'])
    selected_samples_path, selected_anapath, tumor_map = select_samples(vcf_path, config['study'], args.out_dir)
    # -> selected_samples_path: le path du dossier où se trouve les fichiers selectionnés

    # Trie les sample_id par patient_id
    dict_samples = make_dict_samples(selected_anapath)

    os.mkdir(to_import_dir)

    # ~~~~ Partie mutation ~~~~
    use_vcf2maf(args.out_dir, os.path.join(to_import_dir, 'mutations.maf'), selected_samples_path, tumor_map)
    # -> output un .maf dans le dossier à importer: ($to_import_dir/'temp_maf_dir')

    # ~~~~ Partie data ~~~~
    if not os.path.exists(os.path.join(to_import_dir, 'case_lists')):
        os.mkdir(os.path.join(to_import_dir, 'case_lists'))

    # On ouvre trois fichiers à la fois
    with open(os.path.join(to_import_dir, 'data_patients.txt'), 'wb') as fpatients, open(os.path.join(to_import_dir, 'data_samples.txt'), 'wb') as fsamples, open(os.path.join(to_import_dir, 'case_lists', "cases_custom.txt"), 'wb') as fcases:

        en_tete = "#Patient Identifier\tLocalisation\n#Patient Identifier\tLocalisation\n#STRING\tSTRING\n#1\t1\nPATIENT_ID\tLOCALISATION\n"
        fpatients.write(en_tete)

        en_tete = "#Patient Identifier\tSample Identifier\n#Patient Identifier\tSample Identifier\n#STRING\tSTRING\n#1\t1\nPATIENT_ID\tSAMPLE_ID\n"
        fsamples.write(en_tete)

        for patient_id in dict_samples:

            fpatients.write(patient_id + "\t" + config['cancer_study_identifier'] + "\n")

            if len(set(dict_samples[patient_id])) > 1:
                print('Warning: un patient_id: {} est lié à plus de un sample_id'.format(patient_id))
                for sample_id in dict_samples[patient_id]:
                    fsamples.write(patient_id + "\t" + sample_id + "\n")
                    case_list_ids.append(sample_id)
            else:
                sample_id = dict_samples[patient_id][0]
                fsamples.write(patient_id + "\t" + sample_id + "\n")
                case_list_ids.append(sample_id)

        fcases.write("cancer_study_identifier: {}\n".format(config['cancer_study_identifier']))
        fcases.write("stable_id: {}_custom\n".format(config['cancer_study_identifier']))
        fcases.write("case_list_name: {}\n".format(config['case_list']['name']))
        fcases.write("case_list_description: {}\n".format(config['case_list']['description']))
        fcases.write("case_list_ids: ")
        fcases.write("\t".join(case_list_ids))

    # ~~~~ Partie meta ~~~~
    write_meta_files(to_import_dir, config)

    # Partie validation
    if args.report:
        cmd = os.path.expanduser('~') + '/Code/cbioportal/core/src/main/scripts/importer/validateData.py \
        -u http://129.10.28.22:8666/cbioportal/ -s ' + os.path.join(to_import_dir) + '\
         -v -html ReportValidation' + config['cancer_study_identifier'] + '.html'
        argcall = shlex.split(cmd)
        subprocess.call(argcall)
        print("Reports are made in current directory.")
