import json

body_properties = ["case_id", "injury_type", "shape", "number_of_lessions", "distributions", "color"]


def validate_property_exist(property, loaded_body):
    if property in loaded_body:
        if loaded_body[property] is not None:
            return True
        else:
            return False
    else:
        return False
