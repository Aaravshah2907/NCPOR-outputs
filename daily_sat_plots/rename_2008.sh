#!/bin/bash

for file in ./Year_2008_*.png; do
    if [[ -e "$file" ]]; then
        newname="./Year_08_${file#./Year_2008_}"
        mv "$file" "$newname"
    fi
done
