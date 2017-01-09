#!/usr/bin/env bash

# Script which verifies that service running on the provided port is only bound
# to localhost (127.0.0.1)

PORT=$1

OUTPUT=$(sudo netstat -tlpn | grep \:\:\:${PORT}| wc -l)
if [ ${OUTPUT} -eq 1 ]; then
    echo "Service for port ${PORT} is bound on all the interfaces"
    echo ""
    echo $(sudo netstat -tlpn | grep \:\:\:${PORT})
    exit 1
fi

OUTPUT=$(sudo netstat -tlpn | grep 127.0.0.1\:${PORT}| wc -l)
if [ ${OUTPUT} -ne 1 ]; then
    echo "Service not listening on 127.0.0.1:${PORT}"
    exit 1
fi

OUTPUT=$(sudo netstat -tlpn | grep \:${PORT}| wc -l)
if [ ${OUTPUT} -ne 1 ]; then
    echo "Service listening on multiple interfaces / addresses for port ${PORT}"
    echo ""
    echo $(sudo netstat -tlpn | grep \:${PORT})
    exit 1
fi

echo "All good, service only listening on 127.0.0.1:${PORT}"
exit 0
