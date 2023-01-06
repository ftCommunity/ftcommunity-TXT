#!/bin/bash

for tsfile in `find board -name '*_*.ts' -type f`; do
    echo "$tsfile"
    pyfile=${tsfile/_*.ts/.py}
    if [ -e $pyfile ]; then
	pylupdate5 $pyfile -ts $tsfile
	lconvert -i $tsfile -o ${tsfile/.ts/.qm}
    fi
done
