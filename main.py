#!/usr/bin/env python3
import sys
import json
from validation import validate_rules
from engine import evaluate_single_input

def main():
    print("\n" + "="*50)
    print("RULE-BASED DECISION ENGINE")
    print("="*50)
    
    # Validate rules file first
    rules = validate_rules('rules.json')
    if not rules:
        sys.exit(1)
    
    # Ask user for input method
    print("\nInput options:")
    print("1. Run all test cases from input.json (one by one)")
    print("2. Enter single input manually")
    
    choice = input("\nChoose (1 or 2) [default=1]: ").strip()
    
    if choice == '2':
        # Manual input - single case
        print("\n--- Enter Values (press Enter to skip) ---")
        data = {}
        
        amount = input("Enter amount: ").strip()
        if amount:
            try:
                data['amount'] = float(amount)
            except ValueError:
                print("  Invalid number, skipped")
        
        risk = input("Enter risk_score: ").strip()
        if risk:
            try:
                data['risk_score'] = float(risk)
            except ValueError:
                print("  Invalid number, skipped")
        
        vendor = input("Enter vendor_type: ").strip()
        if vendor:
            data['vendor_type'] = vendor
        
        country = input("Enter country: ").strip()
        if country:
            data['country'] = country
        
        if not data:
            print("\nNo input data provided")
            sys.exit(1)
        
        evaluate_single_input(data)
        
    else:
        # Run all test cases from file - ONE BY ONE
        try:
            with open('input.json', 'r') as f:
                file_content = json.load(f)
        except FileNotFoundError:
            print("\nError: input.json not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"\nError: input.json has invalid JSON - {e}")
            sys.exit(1)
        
        # Check if it's the new format with 'inputs' array
        if isinstance(file_content, dict) and 'inputs' in file_content:
            test_cases = file_content['inputs']
            print(f"\nFound {len(test_cases)} test cases")
            
            # Process each test case one by one
            for i, test_case in enumerate(test_cases):
                print(f"\n{'='*50}")
                print(f"TEST CASE {i+1}: {test_case.get('description', 'No description')}")
                
                # Extract data (exclude id and description)
                data = {}
                for key, value in test_case.items():
                    if key not in ['id', 'description']:
                        data[key] = value
                
                evaluate_single_input(data)
                print(f"{'='*50}")
        
        # Old format - single input
        elif isinstance(file_content, dict):
            print("\nFound single input in file")
            evaluate_single_input(file_content)
        
        # List format - multiple inputs without wrapper
        elif isinstance(file_content, list):
            print(f"\nFound {len(file_content)} test cases")
            for i, test_case in enumerate(file_content):
                print(f"\n{'='*50}")
                print(f"TEST CASE {i+1}")
                evaluate_single_input(test_case)
                print(f"{'='*50}")
        
        else:
            print("\nError: Unsupported format in input.json")
            sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExited")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)