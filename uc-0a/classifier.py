"""
UC-0A — Complaint Classifier
Built using RICE → agents.md → skills.md → CRAFT workflow.
"""
import argparse
import csv
import re
import sys

# Severity keywords that must trigger Urgent priority
SEVERITY_KEYWORDS = ['injury', 'child', 'school', 'hospital', 'ambulance', 'fire', 'hazard', 'fell', 'collapse']

# Allowed categories (exact strings only)
ALLOWED_CATEGORIES = [
    'Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 
    'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage', 'Other'
]

def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    complaint_id = row.get('complaint_id', '')
    description = row.get('description', '').lower()
    
    # Handle missing or empty description
    if not description or description.strip() == '':
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'No description provided',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Determine category based on keywords in description
    category = 'Other'
    reason_words = []
    
    # Pothole detection
    if any(word in description for word in ['pothole', 'pot hole', 'hole in road', 'tyre damage']):
        category = 'Pothole'
        reason_words = [word for word in ['pothole', 'pot hole', 'hole in road', 'tyre damage'] if word in description]
    
    # Flooding detection
    elif any(word in description for word in ['flood', 'flooded', 'flooding', 'water', 'underpass flooded', 'bus stand flooded']):
        category = 'Flooding'
        reason_words = [word for word in ['flood', 'flooded', 'flooding', 'water'] if word in description]
    
    # Drain Blockage detection
    elif any(word in description for word in ['drain blocked', 'drain blockage', 'blocked drain', 'clogged drain']):
        category = 'Drain Blockage'
        reason_words = [word for word in ['drain blocked', 'drain blockage', 'blocked drain', 'clogged drain'] if word in description]
    
    # Streetlight detection
    elif any(word in description for word in ['streetlight', 'street light', 'light out', 'lights out', 'flickering', 'sparking']):
        category = 'Streetlight'
        reason_words = [word for word in ['streetlight', 'street light', 'light out', 'lights out', 'flickering', 'sparking'] if word in description]
    
    # Waste detection
    elif any(word in description for word in ['garbage', 'waste', 'trash', 'rubbish', 'overflowing bins', 'dumped']):
        category = 'Waste'
        reason_words = [word for word in ['garbage', 'waste', 'trash', 'rubbish', 'overflowing bins', 'dumped'] if word in description]
    
    # Noise detection
    elif any(word in description for word in ['noise', 'music', 'loud', 'playing music']):
        category = 'Noise'
        reason_words = [word for word in ['noise', 'music', 'loud', 'playing music'] if word in description]
    
    # Road Damage detection
    elif any(word in description for word in ['road surface cracked', 'road cracked', 'sinking', 'footpath tiles broken', 'broken footpath']):
        category = 'Road Damage'
        reason_words = [word for word in ['road surface cracked', 'road cracked', 'sinking', 'footpath tiles broken', 'broken footpath'] if word in description]
    
    # Heritage Damage detection
    elif any(word in description for word in ['heritage', 'heritage street', 'heritage damage']):
        category = 'Heritage Damage'
        reason_words = [word for word in ['heritage', 'heritage street', 'heritage damage'] if word in description]
    
    # Heat Hazard detection
    elif any(word in description for word in ['heat', 'heat hazard', 'hot', 'temperature']):
        category = 'Heat Hazard'
        reason_words = [word for word in ['heat', 'heat hazard', 'hot', 'temperature'] if word in description]
    
    # Dead animal - could be Waste or Other
    elif any(word in description for word in ['dead animal', 'animal not removed']):
        category = 'Waste'
        reason_words = [word for word in ['dead animal', 'animal not removed'] if word in description]
    
    # Manhole cover missing - could be Road Damage or Other
    elif any(word in description for word in ['manhole cover missing', 'manhole', 'missing cover']):
        category = 'Road Damage'
        reason_words = [word for word in ['manhole cover missing', 'manhole', 'missing cover'] if word in description]
    
    # If no clear category match, mark as Other with NEEDS_REVIEW
    if category == 'Other':
        return {
            'complaint_id': complaint_id,
            'category': 'Other',
            'priority': 'Standard',
            'reason': 'Category cannot be determined from description',
            'flag': 'NEEDS_REVIEW'
        }
    
    # Determine priority based on severity keywords
    priority = 'Standard'
    for keyword in SEVERITY_KEYWORDS:
        if keyword in description:
            priority = 'Urgent'
            break
    
    # Build reason citing specific words from description
    if reason_words:
        reason = f"Classified as {category} based on keywords: {', '.join(reason_words[:3])}"
    else:
        reason = f"Classified as {category} based on description content"
    
    # Check for ambiguity - if multiple categories could fit
    category_matches = 0
    for cat in ['Pothole', 'Flooding', 'Streetlight', 'Waste', 'Noise', 'Road Damage', 'Heritage Damage', 'Heat Hazard', 'Drain Blockage']:
        if cat.lower() in description:
            category_matches += 1
    
    flag = ''
    if category_matches > 1:
        flag = 'NEEDS_REVIEW'
    
    return {
        'complaint_id': complaint_id,
        'category': category,
        'priority': priority,
        'reason': reason,
        'flag': flag
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    Handles errors gracefully and produces output even if some rows fail.
    """
    results = []
    error_count = 0
    
    try:
        with open(input_path, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            for row_num, row in enumerate(reader, start=2):  # start=2 because header is row 1
                try:
                    result = classify_complaint(row)
                    results.append(result)
                except Exception as e:
                    error_count += 1
                    print(f"Error processing row {row_num}: {e}", file=sys.stderr)
                    # Add error row to maintain output structure
                    results.append({
                        'complaint_id': row.get('complaint_id', f'ERROR_ROW_{row_num}'),
                        'category': 'Other',
                        'priority': 'Standard',
                        'reason': f'Processing error: {str(e)}',
                        'flag': 'NEEDS_REVIEW'
                    })
    
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        raise
    
    # Write output CSV
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            fieldnames = ['complaint_id', 'category', 'priority', 'reason', 'flag']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        raise
    
    if error_count > 0:
        print(f"Warning: {error_count} rows had processing errors", file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
