#!/bin/bash
# test for terminal from https://gist.github.com/1966557, it's a bashism

# Don't output lines with these strings
GREP_STRING="Rescan (parallel)\|^:" 
# SED_NO_PRINTGCDATESTAMPS will strip -XX:+PrintGCDateStamps output from the log. Requires passing -r to GNU sed
SED_NO_PRINTGCDATESTAMPS="[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}\+0000: " 


SEDFLAG=
OUTPUT_FILENAME=fixed-gc.vgc

# GNU sed needs -r, BSD sed needs -E
# Macports' gsed is GNU sed, OS X default sed is BSD, so this test works
function sedflag () {
  case `uname` in
    Linux)
      SEDFLAG='-r'
      ;;
    Darwin)
      SEDFLAG='-E'
      ;;
  esac
}

function assembleOutputFilename() {
RENAME_PATTERN="s/-gc\(.*\).log/\1.vgc/g"
  if [[ $1 =~ .*-gc*.log ]]; then
    OUTPUT_FILENAME=`echo $1 | sed "$RENAME_PATTERN"`
  fi
  if [[ -n $2 ]]; then
    OUTPUT_FILENAME=$2
  fi
}

if [[ -t 0 ]]; then # Reading from a terminal
  sedflag
  assembleOutputFilename $1 $2
  cat -vet $1 | grep -v "\^@" | grep -v "$GREP_STRING" | sed $SEDFLAG  -e 's/\$//g' -e 's/'"$SED_NO_PRINTGCDATESTAMPS"'//g' > $OUTPUT_FILENAME
  echo "Wrote output to $OUTPUT_FILENAME"
else
  # default behavior, mostly same as old script
  echo $OUTPUT_FILENAME
  cat -vet | grep -v "$GREP_STRING" | sed $SEDFLAG -e 's/\$//g' -e 's/'"$SED_NO_PRINTGCDATESTAMPS"'//g'  > $OUTPUT_FILENAME
fi
