"""
    @module settings
    Configuration options for builders
"""
import os


## Path of the docker image used for building debian source ##
DEBIAN_SOURCE_BUILDING_IMAGE = os.path.abspath("../dockerfiles/debian-source-build")

## Wildcard used fo matching the orig tarball file ##
ORIG_TARBALL_FILE_WILDCARD = "*ori.tar.gz"

## Wildcard used for matching the quilt format based patch file ##
PATCH_FILE_WIDLCARD = "*.tar.xz"

## Wildcard used for matching the source control files(.dsc) ##
SOURCE_CONTROL_FILE_WILDCARD = "*.tar.dsc"

## Wildcard used for matching the path of the source directory ##
SOURCE_DIRECTORY_WILDCARD = "syslog-ng-*"

## Path of the docker image used for building source tarball ##
SOURCE_TARBALL_BUILDING_IMAGE = os.path.abspath("../dockerfiles/source-tarball-build")

## Wildcard used for matching the path of the source tarball ##
TARBALL_FILE_WILDCARD = "syslog-ng_*"