#!/bin/sh

if [ -f "/app/maybe_unhealthy" ]; then
    echo "unhealthy"
    exit 1;
else
    echo "healthy"
    exit 0;
fi