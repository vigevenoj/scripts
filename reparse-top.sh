#! /bin/bash
awk 'FNR < 7 { print $0;} FNR == 7 {$1=sprintf("%s (HEX)", $1); print $0 }  FNR > 7 { $1=sprintf("%d (0x%x)", $1, $2); print $0}' "$@"
