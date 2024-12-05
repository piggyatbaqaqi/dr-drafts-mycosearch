#!/bin/bash
# Create a directory of symbolic links to the annotated files.
IDIR=$1
RDIR=$2
SDIR=$3
MAXLINES=$4

if [ ! -d ${IDIR} ]; then
	mkdir ${IDIR}
fi

OUTFNAME=SKOL_S
TMP=${RDIR}/temp

for file in ${RDIR}/*/*.ann; do
	# echo ${file}
	annotated_file="$(basename ${file})"
	volume_name="$(basename $(dirname ${file}))"
	ln -s ../${file} ${IDIR}/${OUTFNAME}_${volume_name}_${annotated_file}
done
