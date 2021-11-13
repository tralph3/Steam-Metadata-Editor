#!/bin/sh

# This script will create a deb package for Steam-Metadata-Editor

packageVersion=$(printf "1.r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)")

# Create file structure

mkdir -pv packaging/DEBIAN
mkdir -pv packaging/usr/share/licenses/steam-metadata-editor
mkdir -pv packaging/usr/share/pixmaps/steam-metadata-editor
mkdir -pv packaging/usr/share/applications
mkdir -pv packaging/usr/share/doc/steam-metadata-editor
mkdir -pv packaging/usr/bin


# Copy files to corresponding directories

cp -vf LICENSE packaging/usr/share/licenses/steam-metadata-editor
cp -vf src/img/*.png packaging/usr/share/pixmaps/steam-metadata-editor
cp -vf steam-metadata-editor.desktop packaging/usr/share/applications
cp -vf README.md packaging/usr/share/doc/steam-metadata-editor
cp -vf src/steammetadataeditor packaging/usr/bin


# Create control file

echo "Package: steam-metadata-editor-git
Version: ${packageVersion}
Architecture: all
Maintainer: tralph3
Depends: python3-tk,python3 (>=3.6)
Priority: optional
Homepage: https://github.com/tralph3/Steam-Metadata-Editor
Description: An easy to use GUI that edits the metadata of your Steam Apps" > packaging/DEBIAN/control

# Build the package

dpkg-deb --build packaging

# Rename the package

mv packaging.deb Steam-Metadata-Editor.deb

