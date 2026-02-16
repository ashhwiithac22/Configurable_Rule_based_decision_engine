import json
def check_condition(cond, data):
    field = cond['field']
    operator = cond['operator']
    target = cond['value']
    
    if field not in data:
        return False, f"{field} is not provided"
    val = data[field]
    
    if val is None:
        return False, f"{field} is empty"
    
    try:
        if operator == '==':
            if isinstance(val, str) and isinstance(target, str):
                result = val.lower() == target.lower()
            else:
                result = val == target
                
        elif operator == '!=':
            if isinstance(val, str) and isinstance(target, str):
                result = val.lower() != target.lower()
            else:
                result = val != target
                
        elif operator == 'IN':
            if isinstance(val, str):
                target_lower = [str(t).lower() for t in target]
                result = val.lower() in target_lower
            else:
                result = val in target
                
        elif operator == 'NOT IN':
            if isinstance(val, str):
                target_lower = [str(t).lower() for t in target]
                result = val.lower() not in target_lower
            else:
                result = val not in target
                
        elif operator == '>':
            result = val > target
        elif operator == '<':
            result = val < target
        elif operator == '>=':
            result = val >= target
        elif operator == '<=':
            result = val <= target
        else:
            return False, f"Unknown operator {operator}"
        
        val_display = f"'{val}'" if isinstance(val, str) else val
        target_display = f"'{target}'" if isinstance(target, str) and operator not in ['IN', 'NOT IN'] else target
        
        return result, f"{val_display} {operator} {target_display}"
    
    except TypeError:
        return False, f"Cannot compare {type(val).__name__} with {type(target).__name__}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_group(group, data):
    results = []
    
    for cond in group['conditions']:
        if 'group' in cond:
            res, msg, sub = check_group(cond['group'], data)
            results.append({
                'text': f"Group ({cond['group']['logic']})",'result': res,'details': sub
            })
        else:
            res, msg = check_condition(cond, data)
            results.append({
                'text': f"{cond['field']} {cond['operator']} {cond['value']}",'result': res,'msg': msg
            })
    
    if group['logic'] == 'AND':
        matched = all(r['result'] for r in results)
    else:
        matched = any(r['result'] for r in results)
    
    return matched, f"Group {group['logic']}", results