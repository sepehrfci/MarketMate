# MarketMate

FastAPI sample service with Docker Compose, GitLab CI/CD, Prometheus, and Grafana.

## Run with Docker Compose

1. Copy `.env.example` to `.env` and set `GRAFANA_ADMIN_PASSWORD` to a strong local password.
2. Set `DOCKERHUB_IMAGE` to the Docker Hub image name, such as `account/marketmate`. Keep `IMAGE_TAG=develop` for the image built from the default branch. Run `docker login` first if the repository is private.
3. Start the services:

   ```bash
   docker compose up -d --pull always
   ```

The app is available through Nginx at `http://localhost:8090`. Prometheus is at `http://localhost:9090` and Grafana at `http://localhost:3000`.

To update only the app to a particular published tag, run:

```bash
IMAGE_TAG=<image-tag> docker compose pull app
IMAGE_TAG=<image-tag> docker compose up -d --no-deps app
```

## CI/CD

The pipeline runs tests, builds the Docker image, pushes both the commit SHA and branch tags to Docker Hub, then scans the published image with Trivy. It only builds and scans images on the default branch. The scan fails on fixable `CRITICAL` vulnerabilities, which prevents the manual deployment jobs from running. Trivy ignores vulnerabilities without an available fix to keep the release gate focused on actionable findings. Add these GitLab CI/CD variables:

- `DOCKERHUB_USERNAME`: Docker Hub username.
- `DOCKERHUB_TOKEN`: Docker Hub access token with permission to push to the image repository; mask it.
- `DOCKERHUB_IMAGE`: image name in `namespace/repository` form.

The Docker Hub image may be public or private; the pipeline logs in with the same Docker Hub credentials before scanning. Review Trivy's findings in the `trivy-image-scan` job log. Fix a finding in the base image or application dependencies, then push a new commit to run the scan again.

Deployment jobs are commented out because this project does not have a staging or production server yet. When a server is available, uncomment the deploy stage and job block in `.gitlab-ci.yml`, then configure the following GitLab variables. Mark `SSH_PRIVATE_KEY` and `SSH_KNOWN_HOSTS` as **File** variables; protect the production values and production environment where appropriate.

| Variable | Purpose |
| --- | --- |
| `STAGING_HOST`, `STAGING_USER`, `STAGING_PATH` | Staging server, SSH user, and directory containing this repository's Compose files and `.env`. |
| `PRODUCTION_HOST`, `PRODUCTION_USER`, `PRODUCTION_PATH` | Production server, SSH user, and directory containing this repository's Compose files and `.env`. |
| `SSH_PRIVATE_KEY` | Private key that can SSH to the deployment hosts. |
| `SSH_KNOWN_HOSTS` | Verified SSH host keys for the deployment hosts. |

The deployment user needs permission to run Docker Compose. Each server must have this repository's Compose and Nginx/monitoring configuration files, a valid `.env` with `GRAFANA_ADMIN_PASSWORD`, and access to pull the Docker Hub image. The deployment job updates only the `app` service. Once enabled, staging is manual, and production is manual after staging succeeds.

Production requires manually starting `deploy-production`. For an additional approval gate, protect the `production` environment in GitLab and restrict who may deploy to it. This sample does not assume that a staging or production server is already available.

## Rollback

Every image is pushed with the short commit SHA as an immutable tag. For a manual rollback after deployment is enabled, start the `rollback-production` job and provide `ROLLBACK_IMAGE_TAG` with the previous known-good commit SHA. The job pulls that image and updates only the app. A manual rollback from the production host can also be done by setting `IMAGE_TAG` to that SHA and running:

```bash
docker compose pull app
docker compose up -d --no-deps app
```

Keep the previous image tag in Docker Hub until the new release has been checked. The Prometheus and Grafana data volumes are separate from the app container and are retained when only `app` is updated.

## Monitoring

Prometheus scrapes the app's `/metrics` endpoint. Grafana is provisioned with Prometheus as its data source and a basic MarketMate dashboard. For centralized logs, Loki can receive logs from the containers through Grafana Alloy or another log collector. Labels such as service and environment make it possible to search logs alongside Prometheus metrics and configure alert rules for error patterns or repeated application failures.

## Security and recovery notes

- Do not commit `.env`, Docker Hub tokens, SSH private keys, or production credentials.
- Use GitLab masked/protected variables for credentials and verified SSH host keys; do not disable SSH host key checking.
- The app runs as a non-root user and has a health check, restart policy, and resource limits in Compose.
- Prometheus and Grafana data use named volumes. Back up those volumes before host maintenance, and verify the previous image tag is available before deploying a release.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for the Nginx 502 investigation steps.
