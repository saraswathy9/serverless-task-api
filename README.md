# Serverless Task Manager API

A simple to-do list API. No servers to manage — AWS runs your code
only when someone calls the API.

## What it uses
- **DynamoDB** — stores the tasks (like a simple database)
- **Lambda** — runs your code (the file `lambda_function.py`)
- **API Gateway** — gives you a web link (URL) that triggers Lambda

## How it works
Someone sends a request to your API link → API Gateway forwards it to
Lambda → Lambda reads/writes DynamoDB → sends the answer back.

---

## Steps to build it

### 1. Create the database
- AWS Console → **DynamoDB** → **Create table**
- Table name: `Tasks`
- Partition key: `id` (type: String)
- Capacity mode: **Provisioned** → Read: `5`, Write: `5` (keeps it free)
- Create table

### 2. Create the permission role
- AWS Console → **IAM** → **Roles** → **Create role**
- Choose **AWS service** → **Lambda**
- Attach policy: `AWSLambdaBasicExecutionRole`
- Name it `TaskManagerLambdaRole` → Create
- Open the role → **Add permissions** → **Create inline policy** → JSON tab
- Paste the contents of `iam-policy.json`

### 3. Create the Lambda function
- AWS Console → **Lambda** → **Create function**
- Name: `taskManagerFunction`
- Runtime: **Python 3.14**
- Use existing role → `TaskManagerLambdaRole`
- Create function
- Paste in the code from `lambda_function.py` → click **Deploy**
- Go to **Configuration → Environment variables** → Add:
  Key = `TABLE_NAME`, Value = `Tasks`

### 4. Create the API
- AWS Console → **API Gateway** → **Create API** → **HTTP API**
- Add integration → choose your Lambda function
- Add these routes, all pointing to your Lambda:
  - POST /tasks
  - GET /tasks
  - GET /tasks/{id}
  - PUT /tasks/{id}
  - DELETE /tasks/{id}
- Create — copy the **Invoke URL** shown

### 5. Test it
Open **AWS CloudShell** (top bar `>_` icon) and run:
```bash
curl -X POST https://YOUR-URL/tasks -H "Content-Type: application/json" -d '{"title":"Test task"}'
curl https://YOUR-URL/tasks
```

---

## Files in this project
- `lambda_function.py` — the code that runs
- `iam-policy.json` — the permissions Lambda needs
- `README.md` — this file
---
