# Deployment Contract

Build once, identify the immutable artifact by commit and SHA-256 digest, and promote that artifact through DEV, TEST/UAT, and PROD. Environment configuration and secrets are external to the artifact. Deployments require auditable identity, retained logs, health validation, rollback criteria, and a documented rollback procedure.

The core CD workflow verifies the same artifact before each stage and uses GitHub environments for the DEV, TEST/UAT, and PROD boundaries. Provider-specific commands belong in a stack overlay and are invoked through the deployment hook.

See [deployment-model.md](deployment/deployment-model.md), [artifact-promotion.md](deployment/artifact-promotion.md), [rollback.md](deployment/rollback.md), and [environment-strategy.md](deployment/environment-strategy.md).
