import fitz  # PyMuPDF

def extract_toc(pdf_path):
    """Extracts the Table of Contents (TOC) from the PDF."""
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    return [{"level": level, "title": title, "page": page} for level, title, page in toc]

def generate_toc_list(toc):
    """Generates a hierarchical list of headers from the TOC."""
    header_list = []
    stack = []  # Track current parent headers

    for entry in toc:
        level, title = entry["level"], entry["title"]

        # Remove deeper levels if necessary
        while len(stack) >= level:
            stack.pop()

        # Add the current title to the hierarchy
        stack.append(title)

        # Store the formatted header path
        header_list.append(", ".join(stack))

    return header_list

# Path to your PDF
pdf_path = "catalog_new.pdf"

# Extract TOC
toc = extract_toc(pdf_path)

# Generate hierarchical header list
header_list = generate_toc_list(toc)

# Save to file
output_txt_path = "toc_headers.txt"
with open(output_txt_path, "w", encoding="utf-8") as f:
    f.write("\n".join(header_list))

# Print output
print(f"TOC headers saved to {output_txt_path}")
