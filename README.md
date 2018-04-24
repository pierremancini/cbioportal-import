# Importer dans cBioportal


## build_study_data.py

Pour importer les fichiers .maf dans cBioportal il faut les organiser dans des dossiers spécifiques et les accompagner de fichiers de métadonnées.

Voir la documentation offichielle: [cbioportal/File-Format](http://cbioportal.readthedocs.io/en/latest/File-Formats.html)

Le script build_study_data.py construit l'arborescence de fichiers d'importation i.e. le dossier contenant les study data.

Le dossier donné par --in-dir doit contenir:
- le fichier de mapping n° anapath  / n° patient
- les fichiers listant les n° anapath de la study
- Un dossier contenant les .vcf, le nom de ce dossier est donné dans build_config.yml

Le script utilise le fichier de configuration build_config.yml. Le build_config.yml fournit par
le dépot dans bitbucket est un exemple.

### Configurer avec build_config.yml

Configurer la construction des données d'importation en modifiant build_config.yml.

- Pour préciser le type de cancer, changer la valeur de meta_study/type_of_cancer

Exemples: coadread pour colon, nsclc pour lung.

- Le(s) fichier(s) listés dans study donne les n° d'échantillons fesant partie de la study. 


### Conversion des .vcf en .maf

Le script build_study_data.py utilise le conteneur de vcf2maf dans la fonction use_vcf2maf:

```bash
docker run -it --rm -v {} -v {} vcf2maf --input-vcf {} --output-maf {} --tumor-barcode-map {} -d --merge-maf
```

L'argument après le premier -v `volume_vep_path_local` correspond au chemin local du volume vep.
Ce volume contient en cache les données de l'archive homo_sapiens_vep_91_GRCh37.tar.gz.

L'argument après le deuxième -v `volume_vcf2maf_path_local` donne le dossier parent du dossier contenant les fichiers .vcf. Après utilisation de vcf2maf les fichiers .maf seront aussi dans ce volume.

L'argument `input` donne le chemin dans le conteneur du dossier contenant les .vcf.
L'argument `output` donne le chemin dans le conteneur du dossier contenant les futurs .maf.


#### Update de la colone TUMOR_BARCODE des .maf

Le script entrypoint.py de vcf2maf rempli les valeurs de la colone TUMOR_BARCODE en fonction des arguments --tumor-id ou --tumor-id-map.


#### Fusion des .maf

Le script entrypoint.py de vcf2maf possède une option --merge-maf qu'il faut utiliser pour l'importation dans cBioportal.


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

Nb: Avant de lancer les commandes de transfert il peut-être important de de vérifier qu'il n'existe
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


### Update d'une study

Pour modifier une study on peut utiliser la procédure d'importation classique sans options supplémentaires.


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
./cbioportal/core/src/main/scripts/importer/cbioportalImporter.py --command remove-study --meta_filename /cbio_studies/{study_name}/meta_study.txt
```

Nb: la commande avec --jvm-args ne marche pas : [https://github.com/cBioPortal/cbioportal/issues/132](https://github.com/cBioPortal/cbioportal/issues/132)