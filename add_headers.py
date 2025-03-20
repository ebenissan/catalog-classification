import json
from collections import defaultdict

def process_sections(sections):
    """
    Groups section headers based on their common prefixes and structures them into a hierarchical format.
    Ensures that all sections retain their full parent path while removing redundancy.
    """
    section_tree = defaultdict(set)

    # Split sections into hierarchical components
    split_sections = [ [part.strip() for part in section.split(",")] for section in sections ]

    # Group sections by their highest-level common prefix
    groups = defaultdict(list)
    for sec in split_sections:
        key = sec[:2]  # Keep first two hierarchy levels as grouping key
        groups[tuple(key)].append(sec)

    formatted_output = []
    
    for key, group in groups.items():
        # Find the longest common prefix for each group
        min_length = min(len(s) for s in group)
        common_prefix = []

        for i in range(min_length):
            current_level = {s[i] for s in group}
            if len(current_level) == 1:
                common_prefix.append(current_level.pop())
            else:
                break
        
        common_prefix_str = " > ".join(common_prefix)
        
        # Gather the remaining unique parts
        unique_suffixes = set()
        for sec in group:
            if len(sec) > len(common_prefix):
                suffix = " > ".join(sec[len(common_prefix):])
                unique_suffixes.add(suffix)
        
        # Build formatted output ensuring that each common prefix is retained separately
        formatted_output.append(common_prefix_str)
        for suffix in sorted(unique_suffixes):
            formatted_output.append(f"- {suffix}")
    
    return "\n".join(formatted_output)

def process_chunks(input_file, output_file):
    """
    Reads chunks from the input JSON file, processes each chunk by prepending a formatted header (derived from the sections)
    to the chunk's text, and writes the updated chunks to the output JSON file.
    """
    with open(input_file, "r", encoding="utf-8") as infile:
        chunks = json.load(infile)
    
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        sections = metadata.get("sections", [])
        if sections:
            # Process sections to get a header string
            header = process_sections(sections)
            # Prepend header and a separator (e.g., two newlines) to the existing text
            chunk["text"] = f"{header}\n\n{chunk['text']}"
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(chunks, outfile, indent=2, ensure_ascii=False)
    print(f"Processed {len(chunks)} chunks and wrote output to {output_file}")

if __name__ == "__main__":
    # Set your input and output file paths here
    input_file = "classified_catalog_agent_new.json"
    output_file = "catalog_with_headers_new_2.json"
    process_chunks(input_file, output_file)
