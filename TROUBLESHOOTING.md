# Troubleshooting: Nginx returns 502

A 502 from Nginx usually means Nginx could not get a valid response from the upstream app. Check the path from the outside in, and use the Compose service names on the internal network.

## 1. Check service state and health

```bash
docker compose ps
docker compose logs --tail=100 app
docker compose logs --tail=100 nginx
```

Look for an unhealthy or restarting app, a Python startup/import error, or Nginx messages such as `connect() failed (111: Connection refused)` and `host not found in upstream`.

## 2. Check the app directly from inside the Compose network

```bash
docker compose exec nginx wget -S -O- http://app:8000/health
docker compose exec nginx wget -S -O- http://app:8000/api/status
```

If these fail, inspect the app logs and health check. Confirm Uvicorn listens on `0.0.0.0:8000`, the Compose service is named `app`, and the container reports port 8000:

```bash
docker compose exec app sh -c 'python -c "import urllib.request; print(urllib.request.urlopen(\"http://127.0.0.1:8000/health\").read().decode())"'
docker inspect "$(docker compose ps -q app)" --format '{{json .State.Health}}'
```

## 3. Check Nginx configuration and the public endpoint

```bash
docker compose exec nginx nginx -t
docker compose exec nginx cat /etc/nginx/conf.d/default.conf
curl -i http://localhost:8090/health
```

The Nginx upstream should use `app:8000`, not `localhost:8000`: inside the Nginx container, `localhost` refers to Nginx itself. Confirm both services are attached to the same Compose network and that the configured upstream port matches the app's listening port.

## 4. Apply the fix and check recovery

After fixing the app startup, service name, port, network, or Nginx upstream, recreate the affected service and recheck health and logs:

```bash
docker compose up -d app nginx
docker compose ps
docker compose logs --tail=50 app nginx
curl -i http://localhost:8090/health
```

For a failed app release, deploy the previous known-good image tag as described in the rollback section of the README.

## Prevention

- Keep the app's Compose health check and have Nginx wait for the app to become healthy.
- Use the Compose service name and container port for internal requests.
- Review app and Nginx logs after a deployment and keep image tags tied to commit SHAs for rollback.
- Alert on sustained app health-check failures or a rise in HTTP errors; keep resource limits and restart policies enabled.
