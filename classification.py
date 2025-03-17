import json

# Load the list of hierarchical headers from the TOC file
def load_headers(header_file):
    with open(header_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# Load the JSON data of chunks
def load_chunks(chunk_file):
    with open(chunk_file, "r", encoding="utf-8") as f:
        return json.load(f)

# Save classified chunks to a **new** JSON file
def save_chunks(new_chunk_file, classified_chunks):
    with open(new_chunk_file, "w", encoding="utf-8") as f:
        json.dump(classified_chunks, f, indent=4)
    print(f"\n✅ Classified chunks saved to {new_chunk_file}")

# Display the options for headers and allow user selection
def get_user_selection(headers, start_index):
    print("\n🔹 **Select the appropriate section(s) for this chunk** 🔹")
    print("   (Type 'undo' to go back to the previous chunk)")
    
    end_index = min(start_index + 10, len(headers))  # Show only 10 at a time

    for i in range(start_index, end_index):
        print(f"[{i+1}] {headers[i]}")

    while True:
        user_input = input("\nEnter numbers (e.g. 2-4 or 1,3,5) or type 'undo': ").strip()

        if user_input.lower() == "undo":
            return "undo"

        selected_indices = []
        try:
            # Handle ranges (e.g., "2-4" → [2,3,4])
            for part in user_input.split(","):
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    selected_indices.extend(range(start, end + 1))
                else:
                    selected_indices.append(int(part))

            # Convert to zero-based index
            selected_indices = [i - 1 for i in selected_indices if 0 <= i - 1 < len(headers)]
            
            if selected_indices:
                return selected_indices  # Return valid selections

        except ValueError:
            print("❌ Invalid input. Please enter numbers separated by commas or a range like 2-4.")

# Main function to classify chunks
def classify_chunks(chunk_file, header_file):
    headers = load_headers(header_file)  # Load the list of headers
    chunks = load_chunks(chunk_file)  # Load the JSON chunks
    classified_chunks = []  # Stores the modified chunks

    last_selected_index = 0  # Track where to start displaying headers
    chunk_index = 0  # Track the current chunk index

    while chunk_index < len(chunks):
        chunk = chunks[chunk_index]

        print("\n" + "=" * 80)
        print(f"📜 Chunk #{chunk['metadata']['chunk_number']}")
        print("-" * 80)
        print(chunk["text"])
        print("=" * 80)

        # Get user selection of headers
        selected_indices = get_user_selection(headers, last_selected_index)

        if selected_indices == "undo":
            if classified_chunks:
                # Remove the last classified chunk
                last_selected_index = classified_chunks[-1]["metadata"].get("last_selected_index", 0)
                classified_chunks.pop()
                chunk_index -= 1
                print("\n🔄 **Undo successful! Returning to previous chunk...**")
            else:
                print("❌ No previous chunk to undo!")
            continue

        selected_headers = [headers[i] for i in selected_indices]

        # Add selected headers to the chunk
        chunk["metadata"]["section"] = selected_headers
        chunk["metadata"]["last_selected_index"] = max(selected_indices) if selected_indices else last_selected_index
        classified_chunks.append(chunk)

        # Save progress after each classification
        save_chunks(chunk_file, classified_chunks)

        # Update for next chunk
        last_selected_index = chunk["metadata"]["last_selected_index"]
        chunk_index += 1

    print("\n🎉 **All chunks classified successfully!**")

# File paths (update these accordingly)
chunk_file = "catalog.json"  # JSON file containing chunks
header_file = "toc_headers.txt"  # Text file with TOC headers
output_file = "classified_catalog.json"

# Run classification process
classify_chunks(chunk_file, header_file)
