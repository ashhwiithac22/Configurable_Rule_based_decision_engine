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
    all_rules_checked = []
    
    for rule in rules:
        results = []
        
        for cond in rule['conditions']:
            if 'group' in cond:
                matched, msg, sub = check_group(cond['group'], data)
                results.append({'text': f"Group ({cond['group']['logic']})", 'result': matched,'details': sub })
            else:
                matched, msg = check_condition(cond, data)
                results.append({'text': f"{cond['field']} {cond['operator']} {cond['value']}",'result': matched,
                    'msg': msg
                })
        
        if rule['logic'] == 'AND':
            rule_matched = all(r['result'] for r in results)
        else:
            rule_matched = any(r['result'] for r in results)

        all_rules_checked.append({
            'rule_id': rule['id'],
            'decision': rule['decision'],
            'logic': rule['logic'],
            'matched': rule_matched,
            'results': results
        })
        
        if rule_matched:
            print(f" Decision: {rule['decision']}")
            print(f" Rule: {rule['id']}")
            print("\n Explanation:")

            if rule['logic'] == 'AND':
                print(f"This rule uses AND logic, which means ALL conditions must be true.")
            else:
                print(f"This rule uses OR logic, which means AT LEAST ONE condition must be true.")
            
            print("\n Analysis:")
            
            passed_count = 0
            total_count = 0

            def print_condition_details(results, indent=0, prefix=""):
                nonlocal passed_count, total_count
                for i, r in enumerate(results):
                    total_count += 1
                    if r['result']:
                        passed_count += 1
                    
                    spaces = "    " * indent
                    if 'details' in r:
                        print(f"\n{spaces} {r['text']}:")
                        if r['result']:
                            print(f"{spaces} All conditions satisfied")
                        else:
                            print(f"{spaces} This group was not satisfied")
                        print_condition_details(r['details'], indent + 1)
                    else:
                        field_name = r['text'].split()[0]
                        status = " Passed" if r['result'] else "Failed"
                        print(f"{spaces}• Condition: {r['text']}")
                        print(f"{spaces}  Result: {status}")
                        print(f"{spaces}  Details: {r.get('msg', 'No details available')}")
                        print()
            
            print_condition_details(results)

            print(f"\n Summary:")
            print(f" Total conditions checked: {total_count}")
            print(f" Conditions passed: {passed_count}")
            print(f" Conditions failed: {total_count - passed_count}")
            
            print(f"\n Why this rule matched?:")
            if rule['logic'] == 'AND':
                if passed_count == total_count:
                    print(f" All {total_count} conditions were satisfied, so the rule matched.")
                else:
                    print(f"This should not happen in matched rule")
            else: 
                if passed_count >= 1:
                    print(f"At least one condition ({passed_count}) was satisfied, so the rule matched.")
                else:
                    print(f"This should not happen in matched rule")

            print(f"\n Decision Meaning:")
            if rule['decision'] == 'APPROVE':
                print(" Approve: This transaction is considered safe and can be processed automatically.")
                print(" The transaction meets all safety criteria and of low risk.")
            elif rule['decision'] == 'REVIEW':
                print(" Review: This transaction needs manual review by a human.")
                print(" While not clearly fraudulent, it has suspicious characteristics that require manual checking.")
            elif rule['decision'] == 'REJECT':
                print("Reject: This transaction is blocked automatically.")
                print("It violates bank policies or shows clear signs of fraud.")
            
            return
    
    print(f" Decision: Reject")

    
    print("\n Detailed Explanation:")
    print("No rules matched with the input")
    
    print("\n Rules checked:")
    for rule_check in all_rules_checked:
        status = "Matched" if rule_check['matched'] else "Did not match"
        print(f"  {rule_check['rule_id']}: {status}")
        
        if not rule_check['matched']:
            failed = []
            for r in rule_check['results']:
                if 'details' in r:
                    for sub in r['details']:
                        if not sub['result']:
                            failed.append(sub['text'].split()[0])
                else:
                    if not r['result']:
                        failed.append(r['text'].split()[0])
            
            if failed:
                print(f"  Reason: Failed because {', '.join(failed)} condition(s) were not satisfied")
    
    print(f"\n Why rejected?:")
    print("The transaction did not match any approval or review rules.")
    print("By default, transactions that don't meet any criteria are rejected for safety.")
    
    print(f"\n Decision Meaning:")
    print(" Reject: This transaction is blocked automatically.")
    print("It doesn't meet any approval and review criteria.")
    print("This is the default, when no rules apply.")