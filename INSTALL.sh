#!/bin/bash

mkdir -pv ~/.local/share/Steam-Metadata-Editor/
mv -vf config ~/.local/share/Steam-Metadata-Editor/
mv -vf img ~/.local/share/Steam-Metadata-Editor/
chmod +x steammetadataeditor
echo "Moving script to /usr/bin"
sudo mv steammetadataeditor /usr/bin

