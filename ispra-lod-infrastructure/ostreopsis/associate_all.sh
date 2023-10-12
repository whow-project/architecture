#!/bin/bash

for csvfile in data/ostreopsis/csv/*.csv; do
    python3 ostreopsis/ostreopsis_associate_to_place.py $csvfile $1
done