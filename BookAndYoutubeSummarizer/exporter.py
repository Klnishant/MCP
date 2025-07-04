import json
import csv

def export_to_json(data, path="output.json"):
    with open(path, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def export_to_csv(data, path="output.csv"):
    with open(path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Chapter", "Summary", "Questions"])
        for chapter, content in data.items():
            writer.writerow([chapter, content["summary"], content["questions"]])