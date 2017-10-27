#!/bin/bash
string=$1
label_pos=$2
file="datamatrix.png"
string="420.2-233-010203040506"
zint -b 71 --square --scale=3 -o"$file" -d420.2-233-010203040506
./PrintLabel DYMO 30333 "$label_pos" "$file" 420.2-233 010203 040506 
exit
