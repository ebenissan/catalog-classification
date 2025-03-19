import json
import pdfplumber
import re

# Path to the uploaded TOC PDF file
pdf_path = "toc.pdf"  # Update with your actual PDF path
toc_output_file = "nested_toc.json"

# Regex pattern to extract TOC entries with page numbers
toc_pattern = re.compile(r"^(\s*)([A-Za-z0-9 &\-,\(\)']+.*?)\s+(\d{1,4})$")  # Matches headers with page numbers

def extract_toc_with_combined_headers(pdf_path):
    toc_list = []
    
    with pdfplumber.open(pdf_path) as pdf:
        top_level = None
        second_level = None

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split("\n")

                for line in lines:
                    match = toc_pattern.match(line.strip())
                    if match:
                        indent, header, page_number = match.groups()
                        indent_level = len(indent) // 2  # Assuming 2 spaces per indent level

                        # Determine hierarchy and build full header name
                        if indent_level == 0:
                            top_level = header
                            second_level = None
                            full_header = header  # Top-level remains unchanged
                        elif indent_level == 1:
                            second_level = header
                            full_header = f"{top_level}, {header}"  # Combine with top-level
                        else:
                            full_header = f"{top_level}, {second_level}, {header}" if second_level else f"{top_level}, {header}"

                        # Store formatted entry
                        toc_list.append({
                            "header": full_header,
                            "page": int(page_number)
                        })

    return toc_list

# Process TOC and generate nested headers
nested_toc_data = extract_toc_with_combined_headers(pdf_path)

# Save to JSON file
with open(toc_output_file, "w", encoding="utf-8") as f:
    json.dump(nested_toc_data, f, indent=4)

print(f"\n✅ Nested TOC with combined headers saved to {toc_output_file}")
