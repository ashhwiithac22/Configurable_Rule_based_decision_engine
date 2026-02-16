import json
def validate_rules(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {filename} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
        return None
    
    if 'rules' not in data:
        print("Error: No 'rules' key found")
        return None
    
    if not isinstance(data['rules'], list):
        print("Error: 'rules' must be a list")
        return None
    
    valid_ops = ['>', '<', '>=', '<=', '==', '!=', 'IN', 'NOT IN']
    
    for i, rule in enumerate(data['rules']):
        if 'id' not in rule:
            print(f"Error: Rule at index {i} missing 'id'")
            return None
        if 'decision' not in rule:
            print(f"Error: Rule {rule.get('id', i)} missing 'decision'")
            return None
        if 'logic' not in rule:
            print(f"Error: Rule {rule['id']} missing 'logic'")
            return None
        if rule['logic'] not in ['AND', 'OR']:
            print(f"Error: Rule {rule['id']} logic must be AND or OR")
            return None
        if 'conditions' not in rule:
            print(f"Error: Rule {rule['id']} missing 'conditions'")
            return None
        if not isinstance(rule['conditions'], list):
            print(f"Error: Rule {rule['id']} conditions must be a list")
            return None
        
        if not validate_conditions(rule['conditions'], rule['id'], valid_ops):
            return None
    
    print("Rules file is valid")
    return data

def validate_conditions(conditions, rule_id, valid_ops):
    """Recursively validate conditions and nested groups"""
    for j, cond in enumerate(conditions):
        if 'group' in cond:
            if not isinstance(cond['group'], dict):
                print(f"Error: Rule {rule_id}: group must be an object")
                return False
            if 'logic' not in cond['group']:
                print(f"Error: Rule {rule_id}: group missing 'logic'")
                return False
            if cond['group']['logic'] not in ['AND', 'OR']:
                print(f"Error: Rule {rule_id}: group logic must be AND or OR")
                return False
            if 'conditions' not in cond['group']:
                print(f"Error: Rule {rule_id}: group missing 'conditions'")
                return False
            if not isinstance(cond['group']['conditions'], list):
                print(f"Error: Rule {rule_id}: group conditions must be a list")
                return False
            
            if not validate_conditions(cond['group']['conditions'], rule_id, valid_ops):
                return False
        else:
            if 'field' not in cond:
                print(f"Error: Rule {rule_id}: condition missing 'field'")
                return False
            if 'operator' not in cond:
                print(f"Error: Rule {rule_id}: condition missing 'operator'")
                return False
            if 'value' not in cond:
                print(f"Error: Rule {rule_id}: condition missing 'value'")
                return False
            if cond['operator'] not in valid_ops:
                print(f"Error: Rule {rule_id}: invalid operator '{cond['operator']}'")
                return False
            if cond['operator'] in ['IN', 'NOT IN'] and not isinstance(cond['value'], list):
                print(f"Error: Rule {rule_id}: {cond['operator']} requires a list value")
                return False
    
    return True