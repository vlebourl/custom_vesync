#!/bin/bash

# Define the new pyvesync version
new_pyvesync_version="$1"

# Update the pyvesync version in requirements.txt
sed -i "s/pyvesync==.*/pyvesync==$new_pyvesync_version/g" requirements.txt

# Update the pyvesync version in manifest.json
sed -i "s/\"pyvesync==.*\"/\"pyvesync==$new_pyvesync_version\"/g" custom_components/vesync/manifest.json

# Increment the version in manifest.json
current_version=$(jq -r '.version' custom_components/vesync/manifest.json)
IFS='.' read -ra version_parts <<< "$current_version"

# Increase the patch version
version_parts[2]=$((${version_parts[2]}+1))

new_version="${version_parts[0]}.${version_parts[1]}.${version_parts[2]}"

# Update the version in manifest.json
jq ".version = \"$new_version\"" custom_components/vesync/manifest.json | sponge custom_components/vesync/manifest.json
