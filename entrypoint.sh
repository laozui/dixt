#!/bin/bash
set -e

echo "=== [1/3] Starting x-tunnel daemon on 127.0.0.1:17170 ==="
/app/x-tunnel -l ws://127.0.0.1:17170 > /tmp/x-tunnel.log 2>&1 &
sleep 1

if [ -n "$TUNNEL_TOKEN" ]; then
    echo "=== [2/3] Starting Cloudflare Tunnel connector ==="
    /app/cloudflared --no-autoupdate --edge-ip-version 4 --protocol quic tunnel run --token "$TUNNEL_TOKEN" > /tmp/cloudflared.log 2>&1 &
else
    echo "=== [2/3] Warning: TUNNEL_TOKEN environment variable not set! ==="
fi

PORT="${PORT:-7860}"
echo "=== [3/3] Starting Web Application on port $PORT ==="
exec gunicorn -w 2 -b 0.0.0.0:"$PORT" app:app
