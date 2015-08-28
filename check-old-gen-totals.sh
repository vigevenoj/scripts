#! /bin/bash
grep "concurrent mark-sweep generation total" "$@" | awk '{ print $5 " " $7 "    " $7/$5 }'
