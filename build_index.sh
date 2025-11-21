#!/bin/bash
IDIR=./index
RDIR=./raw
SDIR=./src
MAXLINES=10000

# Optional Redis parameters
REDIS_URL=""
REDIS_USERNAME=""
REDIS_PASSWORD=""
EMBEDDING_NAME=""
PICKLE_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
	case $1 in
		--redis-url)
			REDIS_URL="$2"
			shift 2
			;;
		--redis-username)
			REDIS_USERNAME="$2"
			shift 2
			;;
		--redis-password)
			REDIS_PASSWORD="$2"
			shift 2
			;;
		--embedding-name)
			EMBEDDING_NAME="$2"
			shift 2
			;;
		--pickle-file)
			PICKLE_FILE="$2"
			shift 2
			;;
		--idir)
			IDIR="$2"
			shift 2
			;;
		*)
			echo "Unknown option: $1"
			echo "Usage: $0 [--idir IDIR] [--redis-url URL] [--redis-username USER] [--redis-password PASS] [--embedding-name NAME] [--pickle-file FILE]"
			exit 1
			;;
	esac
done

if [ ! -d ${IDIR} ]; then
	mkdir ${IDIR}
fi
if [ ! -d ${RDIR} ]; then
	mkdir ${RDIR}
fi

for FILE in ${SDIR}/get_*; do
	echo ${FILE}
	${FILE} ${IDIR} ${RDIR} ${SDIR} ${MAXLINES}
done

echo 'Building index for Dr. Drafts Proposal Test-O-Meter'

# Build command with optional Redis parameters
CMD="python ${SDIR}/compute_embeddings.py ${IDIR}"

if [ -n "$PICKLE_FILE" ]; then
	CMD="$CMD --pickle-file $PICKLE_FILE"
fi

if [ -n "$REDIS_URL" ]; then
	CMD="$CMD --redis-url $REDIS_URL"
fi

if [ -n "$REDIS_USERNAME" ]; then
	CMD="$CMD --redis-username $REDIS_USERNAME"
fi

if [ -n "$REDIS_PASSWORD" ]; then
	CMD="$CMD --redis-password $REDIS_PASSWORD"
fi

if [ -n "$EMBEDDING_NAME" ]; then
	CMD="$CMD --embedding-name $EMBEDDING_NAME"
fi

echo "Running: $CMD"
eval $CMD
