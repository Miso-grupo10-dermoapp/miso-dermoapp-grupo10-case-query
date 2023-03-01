import json
import os

import boto3
import moto
import pytest
from request_validation_utils import body_properties
import app

TABLE_NAME = "dermoapp-patient-cases"


@pytest.fixture
def lambda_environment():
    os.environ[app.ENV_TABLE_NAME] = TABLE_NAME


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def data_table(aws_credentials):
    with moto.mock_dynamodb():
        client = boto3.client("dynamodb", region_name="us-east-1")
        client.create_table(
            KeySchema=[
                {"AttributeName": "case_id", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "case_id", "AttributeType": "S"},
            ],
            TableName=TABLE_NAME,
            BillingMode="PAY_PER_REQUEST"
        )

        yield TABLE_NAME

@pytest.fixture
def load_table(data_table):
    client = boto3.resource("dynamodb")
    table = client.Table(app.ENV_TABLE_NAME)
    body = {
        'case_id': '123',
        'injury_type': 'test_inj',
        'shape': 'shape-test',
        'number_of_lessions': 'lesson_test',
        'distributions': 'test',
        'color': 'test-red'
    }
    table.put_item(Item=body)
def test_givenValidInputRequestThenReturn200AndValidPersistence(lambda_environment, load_table):
    event = {
        "resource": "/patient/{patient_id}/case/{case_id}",
        "path": "/patient/123/case/123",
        "httpMethod": "GET",
        "pathParameters": {
            "patient_id": "123",
            "case_id": "123"
        },
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    assert lambdaResponse['statusCode'] == 200
    data = json.loads(lambdaResponse['body'])
    assert data is not None
    for property in body_properties:
        assert data[property] is not None


def test_givenMissingBodyOnRequestThenReturnError500(lambda_environment, data_table):
    event = {
        "resource": "/patient/{patient_id}/profile",
        "path": "/patient/123/profile",
        "httpMethod": "POST",
        "pathParameters": {
            "patient_id": "123"
        },
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    assert lambdaResponse['statusCode'] == 412
    assert '{"message": "missing or malformed request body"}' in lambdaResponse['body']


def test_givenRequestWithoutPatientIDThenReturnError412(lambda_environment, data_table):
    event = {
        "resource": "/patient/{patient_id}/profile",
        "path": "/patient/profile",
        "httpMethod": "POST",
        "pathParameters": {
        },
        "body": "{\n \"other_field\": \"prof-1\", \"tone_skin\": \"brown\", \"eye_color\": \"blue\",\"hair_coloring\": "
                "\"honey\", \"tan_effect\": \"test\", \"sun_tolerance\": \"low\" \n}",
        "isBase64Encoded": False
    }
    lambdaResponse = app.handler(event, [])

    assert lambdaResponse['statusCode'] == 412
    assert lambdaResponse['body'] == '{"message": "missing or malformed request body"}'
