import json
def check_condition(cond, data):
    field = cond['field']
    operator = cond['operator']
    target = cond['value']

    if field not in data:
        return False, f"{field} not found"
    value = data[field]

    if value is None:
        return False, f"{field} is empty"
    try:
        if operator == '==':
            if type(value) == str and type(target) == str:
                result = value.lower() == target.lower()
            else:
                result = value == target
                
        elif operator == '!=':
            if type(value) == str and type(target) == str:
                result = value.lower() != target.lower()
            else:
                result = value != target
                
        elif operator == '>':
            result = value > target
        elif operator == '<':
            result = value < target
        elif operator == '>=':
            result = value >= target
        elif operator == '<=':
            result = value <= target
            
        elif operator == 'IN':
            if type(value) == str:
                list_items = [str(x).lower() for x in target]
                result = value.lower() in list_items
            else:
                result = value in target
                
        elif operator == 'NOT IN':
            if type(value) == str:
                list_items = [str(x).lower() for x in target]
                result = value.lower() not in list_items
            else:
                result = value not in target
        else:
            return False, f"Unknown operator: {operator}"

        if type(value) == str:
            value_msg = f"'{value}'"
        else:
            value_msg = str(value)
            
        if type(target) == str and operator not in ['IN', 'NOT IN']:
            target_msg = f"'{target}'"
        else:
            target_msg = str(target)
            
        return result, f"{value_msg} {operator} {target_msg}"
        
    except TypeError:
        return False, f"Cannot compare {type(value).__name__} and {type(target).__name__}"
    except Exception as e:
        return False, f"Error: {e}"


def check_group(group, data):
    results = []
    
    for cond in group['conditions']:
        if 'group' in cond:
            matched, msg, details = check_group(cond['group'], data)
            results.append({'text': f"Group ({cond['group']['logic']})",'result': matched,
                'details': details})

        else:
            matched, msg = check_condition(cond, data)
            results.append({'text': f"{cond['field']} {cond['operator']} {cond['value']}",'result': matched,'msg': msg })
    if group['logic'] == 'AND':
        all_passed = True
        for r in results:
            if not r['result']:
                all_passed = False
                break
        matched = all_passed
    else: 
        any_passed = False
        for r in results:
            if r['result']:
                any_passed = True
                break
        matched = any_passed
    
    return matched, f"Group {group['logic']}", results