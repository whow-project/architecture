#!/bin/bash

for xlsfile in data/ostreopsis/xlsx/*.xlsx; do
    python3 ostreopsis/ostreopsis_excel_to_csv.py $xlsfile
done

for csvfile in data/ostreopsis/csv/*.csv; do
    echo $csvfile
    newfile=$(echo "${csvfile// /_}")
    newfile=$(echo "${newfile//Tab./Tab_}")
    newfile=$(echo "${newfile//__/_}")
    echo $newfile
    mv "$csvfile" "$newfile"
done

rm data/ostreopsis/csv/Foglio*.csv
