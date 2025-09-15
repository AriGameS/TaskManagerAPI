# Branch Strategy and CI/CD

This document outlines the branching strategy and CI/CD pipeline for TaskManagerAPI.

## Branch Strategy

### Main Branches

- **`main`** - Production-ready code
  - Protected branch
  - Requires PR reviews
  - Triggers production deployment
  - Only accepts merges from `develop` or `hotfix/*` branches

- **`develop`** - Integration branch for features
  - Protected branch
  - Triggers staging deployment
  - Accepts merges from `feature/*` branches

### Supporting Branches

- **`feature/*`** - Feature development branches
  - Format: `feature/feature-name`
  - Example: `feature/add-user-authentication`
  - Triggers feature pipeline with basic tests
  - Merged into `develop` via PR

- **`hotfix/*`** - Emergency fixes for production
  - Format: `hotfix/issue-description`
  - Example: `hotfix/fix-security-vulnerability`
  - Triggers hotfix pipeline with security scans
  - Can be merged directly into `main` and `develop`

## CI/CD Pipeline

### Workflows

1. **Continuous Integration (`ci.yml`)**
   - Runs on all branches
   - Multi-Python version testing (3.8, 3.9, 3.10, 3.11)
   - Unit tests, integration tests, security scans
   - Docker build and test
   - Code coverage reporting

2. **Pull Request Checks (`pr.yml`)**
   - Runs on PR creation/updates
   - Code quality checks (flake8, black, isort)
   - Test coverage validation (80%+ required)
   - Docker build verification
   - Automated PR comments with results

3. **Deploy to Production (`deploy.yml`)**
   - Runs on `main` branch pushes
   - Builds and pushes Docker images to GitHub Container Registry
   - Deploys to production environment
   - Includes rollback capability

4. **Develop Branch Pipeline (`develop.yml`)**
   - Runs on `develop` branch pushes
   - Deploys to staging environment
   - Runs staging-specific tests

5. **Feature Branch Pipeline (`feature.yml`)**
   - Runs on `feature/*` branches
   - Quick tests and Docker build
   - Validates feature branch readiness

6. **Hotfix Pipeline (`hotfix.yml`)**
   - Runs on `hotfix/*` branches
   - Critical tests and security scans
   - Emergency deployment capability

7. **Scheduled Maintenance (`scheduled.yml`)**
   - Runs weekly (Mondays at 9 AM UTC)
   - Security vulnerability checks
   - Dependency updates
   - Cleanup tasks

8. **Release Pipeline (`release.yml`)**
   - Runs on version tags (v*)
   - Creates GitHub releases
   - Builds and pushes release Docker images
   - Production deployment

## Workflow Triggers

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| CI | Push to any branch, PR | Continuous integration |
| PR | Pull request events | Code review validation |
| Deploy | Push to main | Production deployment |
| Develop | Push to develop | Staging deployment |
| Feature | Push to feature/* | Feature validation |
| Hotfix | Push to hotfix/* | Emergency fixes |
| Scheduled | Weekly schedule | Maintenance |
| Release | Version tags | Release management |

## Quality Gates

### Required Checks
- All tests must pass
- Code coverage ≥ 80%
- Security scans must pass
- Docker build must succeed
- Code quality checks (flake8, black, isort)

### Branch Protection Rules
- `main` branch:
  - Requires PR reviews (2 reviewers)
  - Requires status checks to pass
  - Requires branches to be up to date
  - Restricts pushes to main branch

- `develop` branch:
  - Requires PR reviews (1 reviewer)
  - Requires status checks to pass
  - Restricts pushes to develop branch

## Deployment Environments

### Staging
- Triggered by `develop` branch
- URL: `https://staging.your-domain.com`
- Used for integration testing

### Production
- Triggered by `main` branch
- URL: `https://your-domain.com`
- Requires all quality gates to pass

## Docker Images

### Image Tags
- `latest` - Latest main branch
- `develop` - Latest develop branch
- `v1.0.0` - Specific release version
- `feature/feature-name` - Feature branch images

### Registry
- GitHub Container Registry: `ghcr.io/arigames/taskmanagerapi`

## Monitoring and Notifications

### Success Notifications
- Deployment success messages
- Test pass confirmations
- Release notifications

### Failure Notifications
- Failed test alerts
- Deployment failure notifications
- Security vulnerability alerts

## Getting Started

### For Feature Development
1. Create feature branch: `git checkout -b feature/your-feature-name`
2. Make changes and commit
3. Push branch: `git push origin feature/your-feature-name`
4. Create PR to `develop` branch
5. Wait for CI checks to pass
6. Get code review approval
7. Merge to `develop`

### For Hotfixes
1. Create hotfix branch: `git checkout -b hotfix/issue-description`
2. Make emergency fix and commit
3. Push branch: `git push origin hotfix/issue-description`
4. Create PR to `main` branch
5. Get approval and merge
6. Also merge to `develop`

### For Releases
1. Ensure `develop` is stable
2. Merge `develop` to `main`
3. Create and push tag: `git tag v1.0.0 && git push origin v1.0.0`
4. Release pipeline will automatically create GitHub release
