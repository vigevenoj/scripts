function overview() {
	grep -E "(ERROR|FATAL|SEVERE) (com|org)" "$@" | cut -d ' ' -f5,6 | sort -d | uniq -c | sort -g
}
