#!/usr/bin/env bash
# Download the three handwriting fonts into ./fonts (run once)
set -e
cd "$(dirname "$0")" && mkdir -p fonts && cd fonts
npm pack lxgw-wenkai-webfont@1.7.0 @fontsource/kalam@5.3.0 @fontsource/zcool-kuaile@5.3.0
for f in *.tgz; do mkdir -p "${f%.tgz}"; tar xzf "$f" -C "${f%.tgz}"; rm "$f"; done
