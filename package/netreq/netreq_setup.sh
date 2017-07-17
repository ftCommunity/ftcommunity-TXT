#!/bin/sh
# set up the iptables rules for netreq
PERMFILE=/etc/netreq_permissions

# start with a clean setup
iptables -F
iptables -X

# accept anything on loopback
iptables -A INPUT -i lo -j ACCEPT

# set rules from /etc/netreq_permissions
if [ -f $PERMFILE ]; then
    while read p; do
	p=$(echo $p | cut -d'#' -f1)
	type=$(echo $p | cut -d" " -f1 | tr '[:upper:]' '[:lower:]')
	hwaddr=$(echo $p | cut -d" " -f2 | tr '[:upper:]' '[:lower:]')
	if [ "${type:0:1}" == "a" ]; then
	    iptables -A INPUT -m mac --mac-source $hwaddr -j ACCEPT
	fi
	if [ "${type:0:1}" == "d" ]; then
	    iptables -A INPUT -m mac --mac-source $hwaddr -j DROP
	fi
    done <$PERMFILE
fi
    
# forward any other incoming connection request to netfilter queue 1 
iptables -A INPUT -p tcp -m state --state NEW -j NFQUEUE --queue-num 1
