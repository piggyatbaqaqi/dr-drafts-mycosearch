#!/bin/bash
# Build Debian package for dr-drafts-mycosearch using fpm
#
# Prerequisites:
#   sudo apt install ruby ruby-dev build-essential python3-venv python3-pip python3-build
#   sudo gem install fpm
#
# Usage:
#   ./build-deb.sh

set -e

cd "$(dirname "$0")"

VERSION="0.3.0"
PACKAGE="dr-drafts-mycosearch"
WHEEL_DIR="/opt/skol/wheels"

# Build number management - increments with each build
BUILD_NUMBER_FILE=".build-number"
if [ -f "$BUILD_NUMBER_FILE" ]; then
    BUILD_NUMBER=$(cat "$BUILD_NUMBER_FILE")
else
    BUILD_NUMBER=0
fi
BUILD_NUMBER=$((BUILD_NUMBER + 1))
echo "$BUILD_NUMBER" > "$BUILD_NUMBER_FILE"

FULL_VERSION="${VERSION}-${BUILD_NUMBER}"
echo "=== Building Debian package with fpm (${PACKAGE} ${FULL_VERSION}) ==="

# Clean previous builds
rm -rf dist/ build/ *.egg-info deb_dist/ staging/

# Create output and staging directories
mkdir -p deb_dist
mkdir -p staging${WHEEL_DIR}

# Build the wheel
echo "Building Python wheel..."
python3 -m build --wheel --outdir dist/

# Copy wheel to staging area
cp dist/*.whl staging${WHEEL_DIR}/

# Build the deb using fpm from the staging directory
# --no-auto-depends prevents fpm from generating dependencies automatically
fpm -s dir -t deb \
    --name "$PACKAGE" \
    --version "$FULL_VERSION" \
    --license "MIT" \
    --description "State-of-the-art literature search and embedding-based discovery for scientific papers and grant opportunities" \
    --maintainer "La Monte Henry Piggy Yarroll <piggy@acm.org>" \
    --url "https://github.com/piggyatbaqaqi/dr-drafts-mycosearch" \
    --category "python" \
    --architecture all \
    --no-auto-depends \
    --depends python3 \
    --depends python3-venv \
    --depends skol \
    --deb-user root \
    --deb-group root \
    --after-install debian/postinst \
    --before-remove debian/prerm \
    --package "deb_dist/${PACKAGE}_${FULL_VERSION}_all.deb" \
    -C staging \
    .

# Clean up staging
rm -rf staging/

echo "=== Done ==="
echo "Debian package created:"
ls -la deb_dist/*.deb
