#Image for vcf2maf
#Build command: docker build --build-arg VCF2MAF_URL=`curl -sL https://api.github.com/repos/mskcc/vcf2maf/releases | grep -m1 tarball_url | cut -d\" -f4` -t vcf2maf .
#Launch command: docker run -it  --rm vcf2maf

FROM vep_xx
MAINTAINER Y Laizet <y.laizet@bordeaux.unicancer.fr>

ARG VCF2MAF_URL
ENV VCF2MAF_URL ${VCF2MAF_URL}
ENV VCF2MAF_PATH /vcf2maf
COPY entry.py /


WORKDIR $VCF2MAF_PATH
# Dowload vcf2maf release
RUN curl -L -o mskcc-vcf2maf.tar.gz $VCF2MAF_URL && tar -C $VCF2MAF_PATH -zxf mskcc-vcf2maf.tar.gz && cd mskcc-vcf2maf* && mv * ../

# RUN sed -i 's/86_GRCh37/87_GRCh37/' vcf2maf.pl
RUN  apt-get update && apt-get install -y python3
ENTRYPOINT ["python3", "/entry.py"]

#ENV $PERL5LIB=
