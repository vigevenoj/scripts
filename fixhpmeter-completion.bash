_fixhpmeter()
{
	local cur prev opts
	COMPREPLY=()
	cur="${COMP_WORDS[COMP_CWORD]}"
	COMPREPLY=($( compgen -f -X '!*-gc*.log*' -- ${cur} ) )
}
complete -o default -F _fixhpmeter fixhpmeter.sh
