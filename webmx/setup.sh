#!/bin/bash

_CUCKOOMX="$(pwd)/.."
_CUCKOO="$_CUCKOOMX/../cuckoo"

ln -s "$_CUCKOOMX/lib/cuckoomx" "$_CUCKOO/lib/"
ln -s "$_CUCKOOMX/conf/cuckoomx.conf" "$_CUCKOO/conf/"

cp -rf "$_CUCKOOMX/webmx" "$_CUCKOO"