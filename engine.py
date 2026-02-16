import json
from evaluation import check_condition, check_group

def evaluate_single_input(data, input_id=None, description=None):
    if description:
        print(f"\n{description}")
    
    print(f"Input: {data}")
    
    try:
        with open('rules.json', 'r') as f:
            rules_data = json.load(f)
    except FileNotFoundError:
        print("Error: rules.json not found")
        return
    except json.JSONDecodeError:
        print("Error: rules.json has invalid JSON")
        return
    
    rules = rules_data['rules']
    
    for rule in rules:
        results = []
        
        for cond in rule['conditions']:
            if 'group' in cond:
                matched, msg, sub = check_group(cond['group'], data)
                results.append({'text': f"Group ({cond['group']['logic']})",  'result': matched,'details': sub
                })
            else:
                matched, msg = check_condition(cond, data)
                results.append({'text': f"{cond['field']} {cond['operator']} {cond['value']}",'result': matched,'msg': msg
                })
        
        if rule['logic'] == 'AND':
            rule_matched = all(r['result'] for r in results)
        else:
            rule_matched = any(r['result'] for r in results)
        
        if rule_matched:
            print(f"\nDECISION: {rule['decision']}")
            print(f"RULE: {rule['id']}")
            print("\nEXPLANATION:")
            

            conditions_met = []
            for r in results:
                if 'details' in r:
                    for sub_r in r['details']:
                        if sub_r['result']:
                            field = sub_r['text'].split()[0]
                            conditions_met.append(f"{field} condition was satisfied")
                else:
                    if r['result']:
                        field = r['text'].split()[0]
                        conditions_met.append(f"{field} condition was satisfied")
            
            if conditions_met:
                print("This transaction was flagged because:")
                for condition in conditions_met:
                    print(f"  • {condition}")
            
            print(f"\nREASON: The transaction matched rule '{rule['id']}' which requires {rule['logic']} logic.")
            return
    
    print("\nDECISION: REJECT")
    print("This transaction did not match any rules.")