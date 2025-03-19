import fitz  # PyMuPDF
import json

def extract_toc(pdf_path):
    """Extracts the Table of Contents (TOC) from the PDF."""
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    return [{"level": level, "title": title, "page": page} for level, title, page in toc]

def generate_toc_list_with_pages(toc):
    """Generates a hierarchical list of headers with their page numbers."""
    header_list = []
    stack = []  # Track current parent headers

    for entry in toc:
        level, title, page = entry["level"], entry["title"], entry["page"]

        # Remove deeper levels if necessary
        while len(stack) >= level:
            stack.pop()

        # Add the current title to the hierarchy
        stack.append(title)

        # Store the formatted header path along with page number
        header_list.append({
            "header": ", ".join(stack),
            "page": page
        })

    return header_list

# Path to your PDF
pdf_path = "catalog.pdf"
output_json_path = "toc_headers_with_pages.json"

# Extract TOC
toc = extract_toc(pdf_path)

# Generate hierarchical header list with pages
header_list_with_pages = generate_toc_list_with_pages(toc)

# Save to JSON file
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(header_list_with_pages, f, indent=4)

# Print output
print(f"✅ TOC headers with pages saved to {output_json_path}")
