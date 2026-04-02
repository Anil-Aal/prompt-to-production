# skills.md

skills:
  - name: classify_complaint
    description: Classify a single complaint row into category, priority, reason, and flag
    input: dict with keys: complaint_id, date_raised, city, ward, location, description, reported_by, days_open
    output: dict with keys: complaint_id, category, priority, reason, flag
    error_handling: If description is missing or empty, return category: Other, priority: Standard, reason: "No description provided", flag: NEEDS_REVIEW

  - name: batch_classify
    description: Read input CSV, apply classify_complaint to each row, write results CSV
    input: input_path (str) - path to input CSV file, output_path (str) - path to write output CSV
    output: None (writes CSV file to output_path)
    error_handling: If input file cannot be read, raise error. If individual rows fail, log error and continue processing remaining rows. Ensure output CSV is written even if some rows fail.
