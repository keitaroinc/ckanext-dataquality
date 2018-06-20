def validation_options(key, data, errors, context):
    possible_options = ['0', '1', 'enforce']

    if data[key] not in possible_options:
        message = 'The \'{0}\' key must have one of the following options: '\
            '\'0\', \'1\' or \'enforce\'.'.format(key[2])
        errors[key].append(message)
