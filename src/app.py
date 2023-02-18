import json

from db_service import insert_item, get_item
from request_validation_utils import validate_body_params, validate_property_exist
from request_response_utils import return_error_response, return_status_ok

ENV_TABLE_NAME = "dermoapp-patient-cases"


def handler(event, context):
    try:
        print("lambda execution with context {0}".format(str(context)))
        if validate_property_exist("patient_id", event['pathParameters']) and validate_property_exist('body', event):
            if validate_body_params(event['body']):
                patient_id = event['pathParameters']['patient_id']
                response = add_patient_profile(event, patient_id)
                return return_status_ok(response)
        else:
            return return_error_response("missing or malformed request body", 412)
    except Exception as err:
        return return_error_response("cannot proceed with the request error: " + str(err), 500)


def add_patient_profile(request, patient_id):
    parsed_body = json.loads(request["body"])
    parsed_body['patient_id']=  patient_id
    insert_item(parsed_body)
    return get_item("case_id", parsed_body['case_id'])
