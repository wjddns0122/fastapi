GitHub에 넣어야 하는 값
Secrets

Settings > Secrets and variables > Actions > Secrets

AWS_ROLE_TO_ASSUME
Variables

Settings > Secrets and variables > Actions > Variables

AWS_REGION
ECR_REPOSITORY
ECS_CLUSTER
ECS_SERVICE

예시:

AWS_REGION=ap-northeast-2
ECR_REPOSITORY=fastapi-app
ECS_CLUSTER=my-app-cluster
ECS_SERVICE=my-app-service

프로젝트 구조 예시
your-project/
├─ app/
│ └─ main.py
├─ tests/
├─ requirements.txt
├─ Dockerfile
├─ .aws/
│ └─ task-definition.json
└─ .github/
└─ workflows/
└─ deploy-ecs.yml
