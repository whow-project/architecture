#!/bin/bash
for yy in {2018..2019}; do
    for xlsfile in data/ostreopsis/xlsx/*${yy}.xlsx; do
    echo "Processing ${xlsfile}"
        python3.9 ostreopsis/ostreopsis_excel_to_csv.py $xlsfile $yy
    done
done