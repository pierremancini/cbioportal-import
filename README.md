# Importer dans cBioportal


## build_study_data.py

Pour importer les fichiers .maf dans cBioportal il faut les organiser dans des dossiers spécifiques et les accompagner de fichiers de métadonnées.

Voir la documentation officielle: [cbioportal/File-Format](http://cbioportal.readthedocs.io/en/latest/File-Formats.html)

Le script build_study_data.py construit l'arborescence de fichiers d'importation i.e. le dossier contenant les study data.

Le script utilise le fichier de configuration build_config.yml. Le build_config.yml fournit par
le dépot dans bitbucket est un exemple.

### Installation

- Lancer un conteneur de vcf2maf, cf. [documentation vcf2maf](https://bitbucket.org/bergomultipli/vcf2maf/src/default/).

- Préparer le dossier dont le chemin sera donné dans l'argument --in-dir du script. Le dossier doit contenir:

1) Les fichiers listant les n° anapath de la study. Dans ses fichiers on doit avoir un n° anapath par ligne. Nb: Les noms de ces fichiers doivent être dans le fichier de configuration.

2) Le fichier de mapping n° anapath  / n° patient. Doit être un fichier .csv avec en 1er colone le n° anapath et en 2ème colone le n° patient.

3) Un dossier contenant les .vcf. Par default le nom de ce dossier est vcf, il peut être changé dans le fichier de configuration.


### Configurer avec build_config.yml

Configurer la construction des données d'importation en modifiant build_config.yml.

- Préciser le type de cancer. Changer la valeur de meta_study: type_of_cancer: [type of cancer](http://oncotree.mskcc.org/#/home)

Exemples: coadread pour colon, nsclc pour lung.

- Dans le champ study: donner les noms des fichiers listant les n° anapath de la study.

- Le champ anapath_patient: donner le nom du fichier de mapping n° anapath  / n° patient.


#### Configurations optionnelles:

- vcf_folder_name: Le nom du dossier contenant les .vcf

- meta_study: name: correspond au nom de study affiché dans l'interface web.

- cancer_study_identifier: sera le nom du dossier de study.

- Pour les champs meta_study, meta_samples, meta_patients et meta_mutations_extended servent à changer le contenu des fichiers de meta données de la study.
Avant de les changer il faut lire la documentation de cbioportal à propos du format des fichiers de la study: [doc](https://cbioportal.readthedocs.io/en/latest/File-Formats.html#clinical-data).

### Usage

```
python3 build_study_data.py --in-dir IN_DIR --out-dir OUT_DIR [-c CONFIG] [--mv] [--container-name]
```

Le script créer en sortie le dossier OUT_DIR, composé de trois sous-dossiers:

- no-study: contient les .vcf écartés de la study.

- selected_samples: contient les .vcf selectionnés dans la study.

- Le dossier de study. Nb: Ce dossier devra être transféré dans le conteneur cbioportal pour pouvoir l'importer dans l'instance cBioportal (cf. section Commandes d'importation, suppression et rapport d'importation).

L'option -c permet spécifier le chemin du fichier de configuration. Par défault le fichier build_config.yml situe au même niveau que le script sera utilisé.

L'option --mv permet de faire un backup de l'ancienne study en cas de conflit de nom avec la nouvelle study.

L'option --container-name sert à spécifier le nom du conteneur vcf2maf. Par defaut ce nom sera vcf2maf.

### Fonctionnement du script

#### Conversion des .vcf en .maf

Le script build_study_data.py utilise le conteneur de vcf2maf. 

Par default le conteneur utilisé s'appelle vcf2amf mais il est possible de pointer vers on conteneur vcf2maf nommé différement en utilisant l'argument --container-name du script (cf. Usage).

La commande lancée par le script est:


```bash
docker run -it --rm -v {} -v {} {container-name} --input-vcf {} --output-maf {} --tumor-barcode-map {} -d --merge-maf
```

L'argument après le premier -v `volume_vep_path_local` correspond au chemin local du volume vep.
Ce volume contient en cache les données de l'archive homo_sapiens_vep_91_GRCh37.tar.gz.

L'argument après le deuxième -v `volume_vcf2maf_path_local` donne le dossier parent du dossier contenant les fichiers .vcf. Après utilisation de vcf2maf les fichiers .maf seront aussi dans ce volume.

L'argument `input` donne le chemin dans le conteneur du dossier contenant les .vcf.
L'argument `output` donne le chemin dans le conteneur du dossier contenant les futurs .maf.


#### Update de la colone TUMOR_BARCODE des .maf

Le script entrypoint.py de vcf2maf rempli les valeurs de la colone TUMOR_BARCODE en fonction des arguments --tumor-id ou --tumor-id-map.


#### Fusion des .maf

Le script entrypoint.py de vcf2maf possède une option --merge-maf qui est utilisé pour avoir un seul fichier .maf en sortie et permettant ainsi l'importation dans cBioportal.


## Commandes d'importation, suppression et rapport d'importation

### Importation

Une fois les study data contruites il faut mettre le dossier dans le volume du conteneur de cBioportal.

Le conteneur cBioportal peut-être lancer sur k2so sur son noeud de virtualisation kvm01.

Pour transferer le dossier study data sur le noeud de virtualisation on peut

1) Utilisation de scp:

Copie local -> scratch du noeud maitre de k2so
```bash
scp -r {study_dir_path} root@129.10.28.20:/scratch/pmancini/{study_name}
```

Aller sur le noeud maitre
```bash
ssh root@129.10.28.20
```

Copie joeud maitre -> noeud de virtualisation
```bash
cd /scratch/pmancini
scp -r {study_name} root@kvm01:/data/dockerbuilds/cbioportal/studies/{study_name}
```

Nb: Avant de lancer les commandes de transfert il peut être important de vérifier qu'il n'existe
pas de dossier portant le même que le dossier study courant sur les noeuds k2so car les scp semble 
le ne pas réaliser d'overwrite en cas d'homonymes. scp n'affiche aucun warning en cas d'homonymes.

__ou__

1')  Utiliser le script python qui wrap l'utilisations des commandes de transfert:

```python
python3 transfer_study.py --study-path {}
```

Le script transfer_study.py écrase les anciens dossiers portant le même nom que le dossier
study courant.

Nb: La copie automatique des fichiers partagé dans le volume du conteneur présente un bug quand un 
fichier est changer tout en gardant le même nom.


2) Commande dans le conteneur


Une fois dans root@kvm01:/data/dockerbuilds/cbioportal/studies/ le dossier study pourra être monté
automatiquement dans le conteneur car /data/dockerbuilds/cbioportal/studies/ est un volume du conteneur
[Volumes docker](https://docs.docker.com/storage/volumes/#choose-the--v-or---mount-flag).

Lancement du conteneur:
```bash
docker exec -it cbioportal /bin/bash
```

Lancement du script d'importation de l'instance cBioportal:
```bash
cd /
./cbioportal/core/src/main/scripts/importer/metaImport.py -s /cbio_studies/{study_name}/ -o -u http://localhost:8080/cbioportal -v -html /cbio_studies/{report_name}.html
```

3) Redémarer le conteneur:

Sur le noeud de virtualisation

```bash
docker stop cbioportal
docker start cbioportal
```

### Récupération du raport d'importation

1) Transférer le report du noeud de virtualisation vers le noeud maitre:

scp -r root@kvm01:/data/dockerbuilds/cbioportal/studies/{report_name} /scratch/pmancini/cbioportal/reports/{report_name}

2) Transferer le report du scratch du noeud matire en local:

Utiliser le script python:

```python
python3 transfer_reports.py --reports-path {}
```

### Suppression de study dans cBioportal

L'arborescence du dossier d'importation contient un fichier meta_study.txt

On utilise ce fichier meta_study qui doit être situé dans conteneur:

```bash
cd /
./cbioportal/core/src/main/scripts/importer/cbioportalImporter.py --command remove-study --meta_filename /cbio_studies/{study_name}/meta_study.txt
```

Nb: la commande avec --jvm-args ne marche pas : [https://github.com/cBioPortal/cbioportal/issues/132](https://github.com/cBioPortal/cbioportal/issues/132)


### Update d'une study

cBioportal ne possède pas d'option de mise à jour des study. Il faut donc supprimer la study en question puis importer la nouvelle version mise à jour.