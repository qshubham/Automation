#!/bin/bash
function check_pid {
rsync_pid=$(pgrep rsync | wc -l)

if [[ $rsync_pid -gt 0 ]]
then
echo " One or more than 1 Pid found"
exit 1

	if [[ $rsync_pid -eq 0 ]]
	then
	echo " Zero pid found. Rsync is ready to start . Will check for file synchronization status."
	else 
	echo " Not a valid value"
	fi
fi
}
check_pid