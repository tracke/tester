#!/bin/bash
# Demonstrates shells built in ability to split stuff.  Saves on
# using sed and awk in shell scripts. Can help performance.

shopt -o nounset
declare -rx       FILENAME=payroll_2007-06-12.txt

# Splits
declare -rx   NAME_PORTION=${FILENAME%.*}     # Left of .
declare -rx      EXTENSION=${FILENAME#*.}     # Right of .
declare -rx           NAME=${NAME_PORTION%_*} # Left of _
declare -rx           DATE=${NAME_PORTION#*_} # Right of _
declare -rx     YEAR_MONTH=${DATE%-*}         # Left of _
declare -rx           YEAR=${YEAR_MONTH%-*}   # Left of _
declare -rx          MONTH=${YEAR_MONTH#*-}   # Left of _
declare -rx            DAY=${DATE##*-}        # Left of _

clear

echo "  Variable: (${FILENAME})"
echo "  Filename: (${NAME_PORTION})"
echo " Extension: (${EXTENSION})"
echo "      Name: (${NAME})"
echo "      Date: (${DATE})"
echo "Year/Month: (${YEAR_MONTH})"
echo "      Year: (${YEAR})"
echo "     Month: (${MONTH})"
echo "       Day: (${DAY})"
