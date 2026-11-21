"""Score extraction JSON predictions. Standard library only."""
import argparse
import json
from pathlib import Path
from statistics import mean

from .check import prepare_text_for_matching
from .common import load_dataset, save_json


def has_allowed_type(value, allowed_types):
    match value:
        case None:
            return 'null' in allowed_types
        case bool():  # Before int: Python booleans are also integers.
            return 'boolean' in allowed_types
        case str():
            return 'string' in allowed_types
        case int():
            return 'integer' in allowed_types
        case float():
            return 'integer' in allowed_types and value.is_integer()
        case list():
            return 'array' in allowed_types
        case dict():
            return 'object' in allowed_types
        case _:
            return False


def matches_schema(value, spec):
    """Validate the types and object shapes used by this benchmark's schemas."""
    if not has_allowed_type(value, spec['type']):
        return False
    if 'enum' in spec and value not in spec['enum']:
        return False
    if isinstance(value, list):
        return all(matches_schema(item, spec['items']) for item in value)
    if isinstance(value, dict):
        properties = spec['properties']
        return (set(value) == set(properties)
                and all(matches_schema(value[field], child) for field, child in properties.items()))
    return True


def values_match(actual, expected):
    if isinstance(actual, dict) and isinstance(expected, dict):
        return (set(actual) == set(expected)
                and all(values_match(actual[key], expected[key]) for key in expected))
    if isinstance(actual, list) and isinstance(expected, list):
        # Lists are unordered, but each expected item must match exactly once.
        if len(actual) != len(expected):
            return False
        unmatched = list(expected)
        for item in actual:
            index = next((i for i, candidate in enumerate(unmatched)
                          if values_match(item, candidate)), None)
            if index is None:
                return False
            unmatched.pop(index)
        return True
    if isinstance(actual, str) and isinstance(expected, str):
        return prepare_text_for_matching(actual) == prepare_text_for_matching(expected)
    if type(actual) in (int, float) and type(expected) in (int, float):
        return actual == expected
    return type(actual) is type(expected) and actual == expected


def reject_invalid_number(value):
    raise ValueError(f'Invalid JSON number: {value}')


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def parse_json_output(text):
    # Invalid model JSON fails this image instead of stopping the benchmark.
    try:
        output = json.loads(text, object_pairs_hook=reject_duplicate_keys,
                            parse_constant=reject_invalid_number)
        if not isinstance(output, dict):
            raise ValueError('Expected a JSON object')
        return output, None
    except ValueError as error:
        return {}, str(error)


def score_image(text, image_tests):
    output, error = parse_json_output(text)
    properties = image_tests['schema']['properties']
    schema_valid = error is None and matches_schema(output, image_tests['schema'])
    check_results = []
    for check in image_tests['checks']:
        field = check['field']
        present = field in output
        actual = output.get(field)
        accepted = [check['expected'], *check.get('alternatives', [])]
        correct_type = matches_schema(actual, properties[field])
        correct_value = any(values_match(actual, value) for value in accepted)
        passed = present and correct_type and correct_value
        check_results.append({**check, 'actual': actual, 'missing': not present, 'pass': passed})
    return {
        'schema_valid': schema_valid,
        'error': error,
        'checks': check_results,
        'score': mean(check['pass'] for check in check_results),
    }


def score_outputs(outputs, dataset):
    image_results = [
        {'image_id': image_id, **score_image(outputs[image_id], image_tests)}
        for image_id, image_tests in dataset.items()
    ]
    all_checks = [check for image_result in image_results for check in image_result['checks']]
    by_basis = {}
    for basis in ('visible', 'inferred', 'unavailable'):
        selected = [check for check in all_checks if check['basis'] == basis]
        by_basis[basis] = {'passed': sum(check['pass'] for check in selected), 'total': len(selected)}
    return {'metric': 'structured_extraction',
            'score': mean(image_result['score'] for image_result in image_results),
            'passed': sum(check['pass'] for check in all_checks),
            'total': len(all_checks), 'by_basis': by_basis,
            'schema_valid_images': sum(image_result['schema_valid'] for image_result in image_results), 'images': image_results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('outputs', help='Directory containing one JSON file per image, e.g. 01.json')
    parser.add_argument('--image', help='Score one image ID')
    parser.add_argument('--out', help='Save a score report')
    args = parser.parse_args()
    dataset = load_dataset('extract', image_id=args.image)
    outputs = {image_id: (Path(args.outputs) / f'{image_id}.json').read_text()
               for image_id in dataset}
    report = score_outputs(outputs, dataset)
    if args.out:
        save_json(args.out, report)
    for image_result in report['images']:
        for check in image_result['checks']:
            actual = '<missing>' if check['missing'] else json.dumps(check['actual'], ensure_ascii=False)
            print(f"{image_result['image_id']} {'PASS' if check['pass'] else 'MISS'}: {check['field']} = {actual}")
        if not image_result['schema_valid']:
            print(f"{image_result['image_id']} SCHEMA ERROR: {image_result['error'] or 'Missing, extra or incorrectly typed fields'}")
    print(f"Extraction: {report['score']:.1%}; {report['passed']}/{report['total']} fields; "
          f"{report['schema_valid_images']}/{len(dataset)} schema-valid outputs")
    for basis, counts in report['by_basis'].items():
        print(f"{basis}: {counts['passed']}/{counts['total']}")


if __name__ == '__main__':
    main()
