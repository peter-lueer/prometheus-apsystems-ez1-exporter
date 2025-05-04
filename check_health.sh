#!/bin/sh

if [ -f "/app/maybe_unhealthy" ]; then
    echo "unhealthy"
    exit 1;
else
    if pgrep -f exporter.py >/dev/null; then 
        echo "healthy"
        exit 0;
    else 
        echo "unhealthy"
        exit 1;
    fi 
fi