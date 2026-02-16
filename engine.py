import json
from evaluation import check_condition, check_group

def evaluate_single_input(data, input_id=None, description=None):
    if description:
        print(f"\n {description}")
    elif input_id:
        print(f"\n Test Case #{input_id}")
    
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
                results.append({'text': f"Group ({cond['group']['logic']})", 'result': matched,'details': sub
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

            for r in results:
                if 'details' in r:
                    if r['result']:
                        print(f"The {r['text']} was satisfied")
                    else:
                        print(f"The {r['text']} was not satisfied")
                    
                    for sub_r in r['details']:
                        if sub_r['result']:
                            print(f" {sub_r['text']} - This condition passed")
                        else:
                            print(f"{sub_r['text']} - This condition failed because {sub_r.get('msg', '')}")
                else:
                    field_name = r['text'].split()[0] 
                    if r['result']:
                        print(f"{field_name} check passed - {r.get('msg', '')}")
                    else:
                        print(f"{field_name} check failed - {r.get('msg', '')}")

            passed = sum(1 for r in results if r['result'])
            total = len(results)
            
            if rule['logic'] == 'AND':
                print(f"\nREASON: This rule requires ALL conditions to be true. {passed} out of {total} conditions were true, so the rule matched.")
            else:
                print(f"\nREASON: This rule requires ANY condition to be true. {passed} out of {total} conditions were true, so the rule matched.")
            
            return
    
    print("\nDECISION: REJECT")
    print("No rules matched the input")