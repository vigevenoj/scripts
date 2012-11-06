function d2h () {
	printf %s\\n "ibase=10;obase=16;$@" | bc | tr '[:upper:]' '[:lower:]'
}
