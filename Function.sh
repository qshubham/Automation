#!/bin/bash
src_ip= 10.0.0.0
dest_ip= 9.9.9.9
src_file=/cctns_pool/IIF-5
dest_file=/cctns_pool/IIF-5
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
function rsync_start {
rsync_start=$(rsync -auvP $src_file dest_ip:dest_file )
if [[ $? -eq 0 ]]
then
echo " File Copied Successfully "
fi
}

check_pid