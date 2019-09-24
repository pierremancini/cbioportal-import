# Application vcf2maf

## Installation

vcf2maf utilise une image docker de vep pour créer et utiliser un conteneur vep. 

### Build de l'image vep

- Télécharger le Dockerfile de vep:

```bash
hg clone ssh://hg@bitbucket.org/bergomultipli/vcf2maf
```

- Créer l'image docker de vep:

```bash
cd vcf2maf/vep
docker build -t vep_xx .
```

Nb: l'image doit porter le nom de "vep_xx"


### Utilisation de l'image docker officielle


```bash
docker pull ensemblorg/ensembl-vep
```

### Dépendences de vep:

- Creation du dossier de cache:

```bash
cd ..
mkdir -p VEP_volume/cache/.vep
```

- Télécharger le fichier isoform_overrides_uniprot du [dépot github](https://github.com/mskcc/vcf2maf/blob/master/data/isoform_overrides_uniprot) dans vcf2maf/VEP_volume/cache/.vep/ :

```bash
cd VEP_volume/cache/.vep/
wget "https://raw.githubusercontent.com/mskcc/vcf2maf/master/data/isoform_overrides_uniprot" 
```
- Télécharger la release_{num_version} depuis ftp://ftp.ensembl.org/pub/release-{num_version}/variation/VEP/homo_sapiens_merged_vep_{num_version}.tar.gz. Avec par exemple, num_version = 91 ou 91_CRCh37.

```bash
wget "ftp://ftp.ensembl.org/pub/release-91/variation/VEP/homo_sapiens_merged_vep_91_GRCh37.tar.gz"
```                              

- Extraire homo_sapiens_merged_vep_91_GRCh37.tar.gz dans VEP_volume/cache/.vep/homo_sapiens/ :

```bash
tar -xzvf homo_sapiens_merged_vep_91_GRCh37.tar.gz
mv homo_sapiens_merged homo_sapiens
```

- Télécharger les fichiers ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz.tbi et ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz.tbi depuis [broadinstitute ftp](ftp://ftp.broadinstitute.org/pub/ExAC_release/release0.3.1/subsets/) dans le dossier vcf2maf/VEP_volume/cache/.vep/ :

```bash
wget "ftp://ftp.broadinstitute.org/pub/ExAC_release/release0.3.1/subsets/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz.tbi"
wget "ftp://ftp.broadinstitute.org/pub/ExAC_release/release0.3.1/subsets/ExAC_nonTCGA.r0.3.1.sites.vep.vcf.gz"
```

- Télécharger Homo_sapiens.GRCh{num_version}.dna_sm.primary_assembly.fa.gz depuis ftp://ftp.ensembl.org/pub/release-{num_version}/fasta/homo_sapiens/dna/ le placer dans VEP_volume/cache/.vep/homo_sapiens/{num_version}/ :

```bash
cd homo_sapiens/91_GRCh37
wget "ftp://ftp.ensembl.org/pub/release-75/fasta/homo_sapiens/dna/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa.gz"
```


### Build de l'image vcf2maf

```bash
cd vcf2maf/vcf2maf
docker build --build-arg VCF2MAF_URL=`curl -sL https://api.github.com/repos/mskcc/vcf2maf/releases | grep -m1 tarball_url | cut -d\" -f4` -t vcf2maf .
```

## Exemples d'utilisisation

### Convertion d'un seul fichier

```bash
docker run -it --rm -v ~/Code/mydockerbuild/vcf2maf/VEP_volume/cache/.vep:/root/.vep -v ~/Code/mydockerbuild/vcf2maf/volume_data:/data vcf2maf --input-vcf /data/dossier_test --output-maf /data/out_merge_test.maf
```

### Préciser la valeur de la colone Tumor_Sample_Barcode

On utilise l'option --tumor-barcode

```bash
docker run -it --rm -v ~/Code/mydockerbuild/vcf2maf/VEP_volume/cache/.vep:/root/.vep -v ~/Code/mydockerbuild/vcf2maf/volume_data:/data vcf2maf --input-vcf /data/dossier_test --output-maf /data/out_merge_test.maf --tumor-barcode NOM_test
```


### Convertion des fichiers d'un dossier

On utilise l'option -d (d pour dossier)


```bash
docker run -it --rm -v ~/Code/mydockerbuild/vcf2maf/VEP_volume/cache/.vep:/root/.vep -v ~/Code/mydockerbuild/vcf2maf/volume_data:/data vcf2maf --input-vcf /data/dossier_test --output-maf /data/out_merge_test.maf -d
```

### Assigner une valeur Tumor_Sample_Barcode à chaque fichiers du dossier

On utilise l'option --tumor-barcode-map

```bash
docker run -it --rm -v ~/Code/mydockerbuild/vcf2maf/VEP_volume/cache/.vep:/root/.vep -v ~/Code/mydockerbuild/vcf2maf/volume_data:/data vcf2maf --input-vcf /data/dossier_test --output-maf /data/out_merge_test.maf -d --tumor-barcode-map /data/tumor_id.tsv 
```

### Option de concaténation des fichiers maf

On utilise l'option --merge-maf

```bash
docker run -it --rm -v ~/Code/mydockerbuild/vcf2maf/VEP_volume/cache/.vep:/root/.vep -v ~/Code/mydockerbuild/vcf2maf/volume_data:/data vcf2maf --input-vcf /data/dossier_test --output-maf /data/out_merge_test.maf -d --tumor-barcode-map /data/tumor_id.tsv --merge-maf
```