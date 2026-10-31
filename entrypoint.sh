#!/bin/bash
set -e

echo "=== [1/3] Starting x-tunnel daemon on 127.0.0.1:17170 ==="
/app/x-tunnel -l ws://127.0.0.1:17170 > /tmp/x-tunnel.log 2>&1 &
sleep 1

TOKEN="${TUNNEL_TOKEN:-eyJhIjoiYWRhM2M0OGM0NDYwZmEwZTI2MTU3NTQ1NDU2M2E4YjgiLCJzIjoiVlliZWF1L2syaE5ZbjRmVVNFYXZxQ3pSRDAzRnBTTVY0clJiTU1BN3NjST0iLCJ0IjoiYzg1YzcxYWMtYjE2YS00YWQxLWFlYTItNDA4OGI3YmU2MWM1In0=}"

if [ -n "$TOKEN" ]; then
    echo "=== [2/3] Starting Cloudflare Tunnel connector ==="
    /app/cloudflared --no-autoupdate --edge-ip-version 4 --protocol quic tunnel --url http://127.0.0.1:17170 run --token "$TOKEN" > /tmp/cloudflared.log 2>&1 &
else
    echo "=== [2/3] Warning: TUNNEL_TOKEN environment variable not set! ==="
fi

PORT="${PORT:-7860}"
echo "=== [3/3] Starting Web Application on port $PORT ==="
exec gunicorn -w 2 -b 0.0.0.0:"$PORT" app:app
