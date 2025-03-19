import json

# Input and output file paths
toc_input_file = "toc_headers_with_pages.json"  # Original TOC with single-page numbers
toc_output_file = "toc_headers_with_page_ranges.json"  # Output TOC with expanded page ranges

def expand_toc_page_ranges(toc_input_file):
    with open(toc_input_file, "r", encoding="utf-8") as f:
        toc_data = json.load(f)

    expanded_toc = []
    
    for i, entry in enumerate(toc_data):
        start_page = entry["page"]
        next_start_page = toc_data[i + 1]["page"] if i + 1 < len(toc_data) else None

        # Assign range: Current start page → Page before the next section starts
        end_page = (next_start_page) if next_start_page and next_start_page > start_page else start_page  # Default to single-page section if no next header

        expanded_toc.append({
            "header": entry["header"],
            "pages": list(range(start_page, end_page + 1))
        })

    return expanded_toc

# Generate expanded TOC
expanded_toc_data = expand_toc_page_ranges(toc_input_file)

# Save to JSON file
with open(toc_output_file, "w", encoding="utf-8") as f:
    json.dump(expanded_toc_data, f, indent=4)

print(f"\n✅ Expanded TOC with page ranges saved to {toc_output_file}")
