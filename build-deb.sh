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

echo "=== Building Debian package with fpm ==="

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
    --version "$VERSION" \
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
    --package "deb_dist/${PACKAGE}_${VERSION}_all.deb" \
    -C staging \
    .

# Clean up staging
rm -rf staging/

echo "=== Done ==="
echo "Debian package created:"
ls -la deb_dist/*.deb
