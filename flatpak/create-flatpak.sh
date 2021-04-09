#!/bin/sh
flatpak-builder .flatpak-build-dir flatpak/com.github.tralph3.Steam-Metadata-Editor.yml --force-clean --repo=.flatpak-repo
flatpak build-bundle .flatpak-repo Steam-Metadata-Editor.flatpak com.github.tralph3.Steam-Metadata-Editor
