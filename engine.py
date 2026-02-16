import json
from evaluation import check_condition, check_group

def evaluate_single_input(data, input_id=None, description=None):
    """Evaluate a single input against all rules"""
    if description:
        print(f"\n📋 {description}")
    elif input_id:
        print(f"\n📋 Test Case #{input_id}")
    
    print(f"Input: {data}")
    print("-" * 40)
    
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
                results.append({
                    'text': f"Group ({cond['group']['logic']})",
                    'result': matched,
                    'details': sub
                })
            else:
                matched, msg = check_condition(cond, data)
                results.append({
                    'text': f"{cond['field']} {cond['op']} {cond['value']}",
                    'result': matched,
                    'msg': msg
                })
        
        if rule['logic'] == 'AND':
            rule_matched = all(r['result'] for r in results)
        else:
            rule_matched = any(r['result'] for r in results)
        
        if rule_matched:
            print(f"DECISION: {rule['decision']}")
            print(f"RULE: {rule['id']}")
            print("\nEXPLANATION:")
            
            passed = 0
            total = 0
            
            def print_results(results, indent=0):
                nonlocal passed, total
                for r in results:
                    total += 1
                    if r['result']:
                        passed += 1
                    
                    spaces = "  " * indent
                    if 'details' in r:
                        status = "✓" if r['result'] else "✗"
                        print(f"{spaces}{status} {r['text']}")
                        print_results(r['details'], indent + 1)
                    else:
                        status = "✓" if r['result'] else "✗"
                        print(f"{spaces}{status} {r['text']} - {r.get('msg', '')}")
            
            print_results(results)
            print(f"\nREASONING: Rule matched because {passed} of {total} conditions passed under {rule['logic']} logic")
            return
    
    print("DECISION: REJECT")
    print("No rules matched the input")