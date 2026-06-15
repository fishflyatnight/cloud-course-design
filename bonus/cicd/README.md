# Bonus 2: CI/CD

The workflow in `.github/workflows/cicd.yml` builds backend and frontend
images, pushes immutable commit-SHA tags to SWR, and updates the CCE
Deployments. It requires these GitHub repository secrets:

- `SWR_USERNAME`
- `SWR_PASSWORD`
- `KUBECONFIG_B64`

`KUBECONFIG_B64` is the base64-encoded public CCE kubeconfig. It must only be
stored as an encrypted GitHub Actions secret and never committed.

