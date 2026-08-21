# This is the Lambda function code.
# It handles 4 actions: Create, Read, Update, Delete (CRUD) tasks.
# It talks to a DynamoDB table to save/read the data.

import json
import os
import uuid
import boto3
from datetime import datetime

# Connect to DynamoDB and pick the table (name comes from an
# environment variable we set in the Lambda console)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])


# This function runs every time someone calls the API.
def lambda_handler(event, context):
    method = event['requestContext']['http']['method']   # GET, POST, PUT, DELETE
    task_id = (event.get('pathParameters') or {}).get('id')  # the {id} in the URL, if any

    if method == 'POST':
        return create_task(event)

    if method == 'GET' and task_id:
        return get_task(task_id)

    if method == 'GET':
        return get_all_tasks()

    if method == 'PUT' and task_id:
        return update_task(task_id, event)

    if method == 'DELETE' and task_id:
        return delete_task(task_id)

    return build_response(400, {'error': 'Route not supported'})


# CREATE a new task
def create_task(event):
    data = json.loads(event.get('body') or '{}')   # read what the user sent

    new_task = {
        'id': str(uuid.uuid4()),          # generate a random unique id
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'status': data.get('status', 'pending'),
        'created_at': datetime.utcnow().isoformat()
    }

    table.put_item(Item=new_task)   # save it to DynamoDB
    return build_response(201, new_task)


# READ one task by id
def get_task(task_id):
    result = table.get_item(Key={'id': task_id})
    task = result.get('Item')

    if not task:
        return build_response(404, {'error': 'Task not found'})

    return build_response(200, task)


# READ all tasks
def get_all_tasks():
    result = table.scan()
    return build_response(200, result.get('Items', []))


# UPDATE an existing task
def update_task(task_id, event):
    existing = table.get_item(Key={'id': task_id}).get('Item')
    if not existing:
        return build_response(404, {'error': 'Task not found'})

    data = json.loads(event.get('body') or '{}')

    table.update_item(
        Key={'id': task_id},
        UpdateExpression='SET title = :t, description = :d, #s = :s',
        ExpressionAttributeNames={'#s': 'status'},   # "status" is a reserved word in DynamoDB
        ExpressionAttributeValues={
            ':t': data.get('title', existing.get('title')),
            ':d': data.get('description', existing.get('description')),
            ':s': data.get('status', existing.get('status'))
        }
    )
    return build_response(200, {'message': 'Task updated'})


# DELETE a task
def delete_task(task_id):
    table.delete_item(Key={'id': task_id})
    return build_response(200, {'message': 'Task deleted'})


# Helper: builds the response in the exact format API Gateway expects
def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body)
    }
  
