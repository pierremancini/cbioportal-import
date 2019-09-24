#Image for vep
#Build command: docker build -t vep_xx .
#Launch command: docker run -it --rm -v ~/Code/mydockerbuild/VEP_volume/cache/.vep:/root/.vep vep_xx

FROM ubuntu:16.04

MAINTAINER Y Laizet <y.laizet@bordeaux.unicancer.fr>

ENV VEP_VERSION=87
ENV VEP_PATH=/vep
ENV VEP_DATA=/vep_data

RUN mkdir -p $VEP_PATH && mkdir -p $VEP_DATA

#Requirements
RUN apt-get update && apt-get install -y \
    autoconf \
    automake \
    build-essential \
    cpanminus \
    curl \
    g++ \
    gcc \
    git \
    libarchive-zip-perl \
    libcgi-session-perl \
    libdbi-perl \
    libgsl0-dev \
    libmodule-build-perl \
    libmysqlclient-dev \
    libncurses5-dev \
    make \
    perl \
    samtools \
    tabix \
    unzip \
    wget \
    zlib1g-dev

RUN cpanm CPAN::Meta \
    Archive::Zip \
    Devel::CheckLib \
    DBD::mysql \
    JSON \
    DBD::SQLite \
    Set::IntervalTree \
    LWP \
    LWP::Simple \
    Archive::Extract \
    Archive::Tar \
    CGI \
    Time::HiRes \
    Encode \
    File::Copy::Recursive \
    Perl::OSType \
    Module::Metadata version \
    Bio::Root::Version \
    TAP::Harness

WORKDIR $VEP_PATH
RUN wget https://github.com/Ensembl/ensembl-tools/archive/release/$VEP_VERSION.zip
RUN unzip $VEP_VERSION.zip -d $VEP_PATH && rm $VEP_VERSION.zip
#RUN mkdir -p variant_effect_predictor && unzip $VEP_VERSION.zip -d variant_effect_predictor && rm $VEP_VERSION.zip

#Download and unpack VEP's offline cache for GRCh37
# RUN rsync -zvh rsync://ftp.ensembl.org/ensembl/pub/release-91/variation/VEP/homo_sapiens_vep_91_GRCh37.tar.gz $VEP_DATA
# RUN cat $VEP_DATA/*_vep_91_GRCh37.tar.gz | tar -izxf - -C $VEP_DATA

#ADD ensembl-api.tar.gz .
#RUN wget ftp://ftp.ensembl.org/pub/ensembl-api.tar.gz
#RUN tar zxvf ensembl-api.tar.gz
ENV PERL5LIB=$VEP_PATH:$VEP_PATH/ensembl/modules:$VEP_PATH/ensembl-compara/modules:$VEP_PATH/ensembl-variation/modules:$VEP_PATH/ensembl-funcgen/modules:/usr/lib/x86_64-linux-gnu/perl5

WORKDIR $VEP_PATH/ensembl-tools-release-$VEP_VERSION/scripts/variant_effect_predictor/
#RUN perl INSTALL.pl --AUTO ap --PLUGINS LoF --CACHEDIR $VEP_DATA
#RUN perl INSTALL.pl --AUTO apf --SPECIES homo_sapiens --ASSEMBLY GRCh37 --DESTDIR $VEP_PATH --PLUGINS LoF --CACHEDIR $VEP_DATA
#RUN perl INSTALL.pl --AUTO apf --SPECIES homo_sapiens --ASSEMBLY GRCh37 --DESTDIR $VEP_PATH --PLUGINS LoF
#RUN perl INSTALL.pl --AUTO af --SPECIES homo_sapiens --ASSEMBLY GRCh37 --DESTDIR $VEP_PATH --CACHEDIR $HOME/.vep/
RUN perl INSTALL.pl --AUTO a 

ENV VEP_DIR=$VEP_PATH/ensembl-tools-release-$VEP_VERSION/scripts/variant_effect_predictor
#WORKDIR /opt/variant_effect_predictor/cache/Plugins
#RUN wget https://raw.githubusercontent.com/konradjk/loftee/master/splice_module.pl
