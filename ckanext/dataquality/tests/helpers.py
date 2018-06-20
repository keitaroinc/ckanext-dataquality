def datastore_create_mock(valid=False):

    def _set_value():
        if valid:
            return u'DK1'
        else:
            return 10

    return {
        "fields": [
            {
                "type": "timestamp",
                "id": "Hour",
                "name_of_field": "Hour",
                "unit": "time",
                "size": "17",
                "comment": "test",
                "attribute_description": "A date and time (interval) where the prices are valid",
                "validation_rules": "Always full hours, i.e. minutes are 00",
                "name_of_attribute": "Hour",
                "example": "2012-10-01T02:00Z"

            },
            {
                "type": "text",
                "id": "PriceArea",
                "name_of_field": "PriceArea",
                "size": "3",
                "unit": "text",
                "comment": "DK1 and DK2 is the standard abbreviation for the two Danish price areas",
                "attribute_description": "A date and time (interval) where the prices are valid",
                "validation_rules": "DK1 or DK2",
                "format_regex": "DK1 | DK2",
                "name_of_attribute": "Price area",
                "example": "DK1"

            }
        ],
        "records": [
            {
                "Hour": "2017-01-01 00:00:00",
                "PriceArea": "DK1"
            },
            {
                "Hour": "2017-01-02 00:00:00",
                "PriceArea": _set_value()
            }
        ],
        "force": True,
        "primary_key": "Hour"
    }


def datastore_upsert_mock():
    return {
        'records': [
            {
                "Hour": "2017-01-03 00:00:00",
                "PriceArea": "DK1"
            }
        ],
        'force': True,
        'method': 'insert'
    }
