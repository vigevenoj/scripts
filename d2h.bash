function d2h () {
	echo "ibase=10;obase=16;$@" | bc | tr '[:upper:]' '[:lower:]'
}
