import fitz  # PyMuPDF
import json

def extract_toc(pdf_path):
    """Extracts the Table of Contents (TOC) from the PDF for reference."""
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    return [{"level": level, "title": title.strip(), "page": page} for level, title, page in toc]


def build_toc_tree(toc):
    """Creates a TOC tree with full parent-child relationships."""
    toc_tree = {}  # {header_title: {"level": X, "parent": Y, "full_path": [...]}}
    stack = []

    for entry in toc:
        level, title, _ = entry["level"], entry["title"], entry["page"]

        # Ensure correct hierarchy
        while stack and stack[-1]["level"] >= level:
            stack.pop()  # Remove headers at the same or deeper level

        parent = stack[-1]["title"] if stack else None
        full_path = stack[-1]["full_path"] + [title] if stack else [title]

        toc_tree[title] = {"level": level, "parent": parent, "full_path": full_path}
        stack.append({"title": title, "level": level, "full_path": full_path})

    return toc_tree

def extract_hierarchical_text(pdf_path, toc):
    """Extract text from a PDF and use the TOC tree for hierarchy reference."""
    doc = fitz.open(pdf_path)
    
    toc_tree = build_toc_tree(toc)  # Build TOC hierarchy
    sections = []
    current_text = ""
    current_headers = []  # Now we always get this from the TOC tree

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                spans = line["spans"]
                line_text = " ".join(span["text"] for span in spans if span["text"].strip())

                # Identify bold text (potential headers)
                bold_spans = [span for span in spans if "bold" in span["font"].lower()]
                
                if bold_spans:  # If bold text is detected, check against TOC
                    bold_text = " ".join(span["text"] for span in bold_spans)
                    matching_toc_entry = toc_tree.get(bold_text)

                    if matching_toc_entry:
                        # Save previous section before moving to a new one
                        if current_text.strip():
                            sections.append({
                                "headers": current_headers,  # Use TOC-based headers
                                "text": current_text.strip()
                            })
                            current_text = ""

                        # **FIX: Use TOC Tree to get correct full path**
                        current_headers = matching_toc_entry["full_path"]

                        # Include full line text
                        current_text += " " + line_text.strip()

                else:
                    current_text += " " + line_text.strip()

    # Save last section
    if current_text.strip():
        sections.append({
            "headers": current_headers,  # Use TOC-based headers
            "text": current_text.strip()
        })

    return sections

# Path to your PDF
pdf_path = "catalog_new.pdf"

# Extract TOC for correct hierarchy reference
toc = extract_toc(pdf_path)

# Extract hierarchical text based on TOC structure
structured_sections = extract_hierarchical_text(pdf_path, toc)

# Save to JSON
output_json_path = "structured_catalog_8.json"
with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(structured_sections, f, indent=4)

print(f"Extracted hierarchical sections saved to {output_json_path}")
