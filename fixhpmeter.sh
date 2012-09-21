#!/bin/bash
# test for terminal from https://gist.github.com/1966557

GREP_STRING="Rescan (parallel)"
OUTPUT_FILENAME=fixed-gc.vgc
RENAME_PATTERN="s/-gc\(.*\).log/\1.vgc/g"

if [[ -t 0 ]]; then
	# Reading from a terminal
	if [[ $1 =~ .*-gc.*.log ]]; then
		OUTPUT_FILENAME=`echo $1 | sed "$RENAME_PATTERN"`
	fi
	if [[ -n $2 ]]; then
		OUTPUT_FILENAME=$2
	fi
	cat -vet $1 | grep -v "\^@" | grep -v "$GREP_STRING" | grep -v "^:" | sed 's/\$//g' > $OUTPUT_FILENAME
	echo "Wrote output to $OUTPUT_FILENAME"
else
	# default behavior, mostly same as old script
	cat -vet | grep -v "$GREP_STRING" | grep -v ":^" | sed 's/\$//g'  > $OUTPUT_FILENAME
fi
