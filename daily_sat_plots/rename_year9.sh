#!/bin/bash

for file in ./Year_8_*.png; do
    if [[ -e "$file" ]]; then
        newname="./Year_08_${file#./Year_8_}"
        mv "$file" "$newname"
    fi
done
