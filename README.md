# Importer dans cBioportal


## build_study_data.py

Pour importer les fichiers .maf dans cBioportal il faut les organiser dans des dossiers spécifiques et les accompagner de fichiers de métadonnées.

Voir la documentation offichielle: [cbioportal/File-Format](http://cbioportal.readthedocs.io/en/latest/File-Formats.html)

Le script build_study_data.py construit l'arborescence de fichiers d'importation i.e. le dossier contenant les study data.

Donner en entrée, après l'argument --in-dir, le chemin du dossier contenant les fichiers .vcf à importer dans cBioportal.

Le script utilise le fichier de configuration build_config.yml. Le build_config.yml fournit par
le dépot dans bitbucket est un exemple.


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
__ou__

1')  utiliser le script python qui wrap l'utilisations des commandes de transfert:

```python
python3 transfer_study.py --study-path {}
```

2) Commande dans le conteneur

Lancement du conteneur:
```bash
docker exec -it cbioportal /bin/bash
```

Lancement du script d'importation de l'instance cBioportal:
```bash
cd /
./cbioportal/core/src/main/scripts/importer/metaImport.py -s /cbio_studies/{study_name}/ -o -u http://localhost:8080/cbioportal -v -html /scratch/pmancini/cbioportal/reports/myReportlunglistes.html
```

### Récupération du raport d'importation


### Suppression de study dans cBioportal

