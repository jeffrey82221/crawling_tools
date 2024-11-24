"""
Develop algorithm to find difference between similar element in the list

=> GROUP BY schema and using recursive to find repeat elements (a new `reduce` method)
            => identify the path where all decendent is the same
            => identify the path where all decendent is not the same
"""
import copy
from typing import Dict
import json
from functools import reduce
import pprint
from jsonschema_inference import fit
data = json.load(open('diff_sample.json', 'r'))
tmp_data = []
for instance in data:
    tmp_data.append((fit(instance), instance))
schema_set = sorted(list(set(map(lambda x: x[0], tmp_data))), key=lambda x: len(str(x)), reverse=True)
target_schema = schema_set[0]
pprint.pprint(target_schema)
# Find target data
target_data = [instance for schema, instance in tmp_data if schema == target_schema]
pprint.pprint(target_data)


def merge(instance_a: Dict, instance_b: Dict) -> Dict:
    """
    Compare difference between two element 
    layer by layer.
    Return if they are the same,
    go deeper if they are not the same,
    stop if the leave is reach and replace the difference 
    of leave by schema.
    """
    instance1 = copy.deepcopy(instance_a)
    instance2 = copy.deepcopy(instance_b)
    if instance1 == instance2:
        return instance1
    else:
        if isinstance(instance1, dict):
            if len(instance1) == len(instance2):
                results = dict()
                for key in instance1:
                    results[key] = merge(instance1[key], instance2[key])
                return results
            else:
                raise ValueError(f'records fields not matched: {instance1.keys()} {instance2.keys()}')
        elif isinstance(instance1, list):
            if len(instance1) == len(instance2):
                results = []
                for i in range(len(instance1)):
                    try:
                        results.append(merge(instance1[i], instance2[i]))
                    except IndexError as e:
                        print('instance_a:', instance_a)
                        print('instance_b:', instance_b)
                        raise e
                return results
            else:
                return fit(instance1) | fit(instance2)
        else:
            if isinstance(instance1, (str, int, float, str)) or instance1 is None:
                return fit(instance1) | fit(instance2)
            else:
                return instance1 | fit(instance2)
            
def add_label(reduced_instance: Dict) -> Dict:
    """
    Convert Schema to `?` to represent changeness
    """
    instance = copy.deepcopy(reduced_instance)
    if isinstance(instance, dict):
        for key in instance:
            instance[key] = add_label(instance[key])
        return instance
    elif isinstance(instance, list):
        for i in range(len(instance)):
            instance[i] = add_label(instance[i])
        return instance
    else:
        if isinstance(reduced_instance, (str, int, float, str)) or reduced_instance is None:
            return instance
        else:
            return '???'

    
reduced_data = reduce(lambda a, b: merge(a, b), target_data)
labeled_data = add_label(reduced_data)
print("labeled_data:")
pprint.pprint(labeled_data)