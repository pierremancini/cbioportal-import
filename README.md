# Importer dans cBioportal


## Utilisation de vcf2maf

Avec la commande perl suivante on utilise vcf2maf qui utilise vep:


Le conteneur de vcf2maf utilise un conteneur de vep.


docker run -it --rm -v `volume_vep_path_local`:/root/.vep -v `volume_vcf2maf_path_local`:/data vcf2maf --input-vcf `input` --output-maf `output`

L'argument après le premier -v `volume_vep_path_local` correspond au chemin local du volume vep.

Pour plus de détail sur les commandes du conteneur voir la documentation sur le dépot vcf2maf.


Ce volume contient en cache les données de l'archive homo_sapiens_vep_86_GRCh37.tar.gz. Par defaut vep ira chercher les données dans ce volume.
Néanmoins, si le cache il est possible de demander au conteneur vep de télécharger lui même les données.
Il faut décommenter dans le Dockerfile (de vep) les lignes en dessous de la ligne "Download and unpack VEP's offline cache for GRCh37".

L'argument après le deuxième -v `volume_vcf2maf_path_local` donne le dossier parent du dossier contenant les fichiers .vcf. Après utilisation de vcf2maf les fichiers .maf seront aussi dans ce volume.

L'argument `input` donne le chemin dans le conteneur du dossier contenant les .vcf.
L'argument `output` donne le chemin dans le conteneur du dossier contenant les futurs .maf.


Exemple de construction d'une commande vcf2maf en python:

```python
cmd = "docker run -it --rm -v " + os.path.expanduser('~') + "/Code/mydockerbuild/vcf2maf/VEP_volume/cache/.vep:/root/.vep -v " + os.path.expanduser('~') + "/Code/mydockerbuild/vcf2maf/volume_data:/data vcf2maf --input-vcf " + os.path.join(os.sep, 'data', vcf_folder_name) + " -d --output-maf " + os.path.join(os.sep, 'data', 'temp_maf_dir')
```

### Update de la colone TUMOR_BARCODE des .maf

Le script entrypoint.py de vcf2maf rempli les valeurs de la colone TUMOR_BARCODE en fonction des arguments
--tumor-id ou --tumor-id-map.


### Fusion des .maf

Le script entrypoint.py de vcf2maf possède une option --merge-maf qu'il faut utiliser pour l'importation
dans cBioportal.


## build_study_data.py

Pour importer les fichiers .maf dans cBioportal il faut les organiser dans des dossiers spécifiques et les accompagner de fichiers de métadonnées.

Le script build_study_data.py construit l'arborescence de fichiers d'importation.

Prendre en entrée le chemin du dossier contenant les fichiers .vcf à importer dans cBioportal.



## Commande d'importation et rapport d'importation


Une fois les l'arborescence construite, on peut suivre les instructions de la documentation officielle:

http://cbioportal.readthedocs.io/en/latest/Importer-Tool.html

