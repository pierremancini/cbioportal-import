#Image for vcf2maf
#Build command: docker build -t cbioimporter .
#Launch command: docker run -it --rm -v ~/Code/mydockerbuild/cbioimporter_vol/:/root/cbioimporter_vol cbioimporter

FROM cbioportal/cbioportal

COPY entry_cbioimporter.py /

WORKDIR core/src/main/scripts/importer

ENTRYPOINT ["python", "/entry_cbioimporter.py"]

