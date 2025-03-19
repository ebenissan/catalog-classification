import json
import os

# Load the list of hierarchical headers from the TOC file
def load_headers(header_file):
    with open(header_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# Load the JSON data of chunks
def load_chunks(chunk_file):
    with open(chunk_file, "r", encoding="utf-8") as f:
        return json.load(f)

# Save classified chunks to the output JSON file
def save_chunks(output_file, classified_chunks):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(classified_chunks, f, indent=4)
    print(f"\n✅ Progress saved to {output_file}")

# Find the last saved chunk index and last selected header index
def get_last_saved_index(output_file):
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            classified_chunks = json.load(f)
            if classified_chunks:
                last_selected_index = classified_chunks[-1]["metadata"].get("last_selected_index", 0)
                return len(classified_chunks), last_selected_index  # Resume from next chunk
    return 0, 0  # Start from the beginning

# Display header options, starting from last used section
def get_user_selection(headers, start_index):
    print("\n🔹 **Select the appropriate section(s) for this chunk** 🔹")
    print("   (Type 'undo' to go back, 'save' to save progress and exit)")

    end_index = min(start_index + 10, len(headers))  # Show 10 headers at a time

    for i in range(start_index, end_index):
        print(f"[{i+1}] {headers[i]}")

    while True:
        user_input = input("\nEnter numbers (e.g. 2-4 or 1,3,5) or 'undo'/'save': ").strip().lower()

        if user_input == "undo":
            return "undo"
        elif user_input == "save":
            return "save"

        selected_indices = []
        try:
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
def classify_chunks(chunk_file, header_file, output_file):
    headers = load_headers(header_file)  # Load TOC headers
    chunks = load_chunks(chunk_file)  # Load catalog chunks
    last_saved_index, last_selected_index = get_last_saved_index(output_file)  # Resume from last point

    # If progress exists, load classified chunks; otherwise, start fresh
    classified_chunks = []
    if last_saved_index > 0:
        with open(output_file, "r", encoding="utf-8") as f:
            classified_chunks = json.load(f)

    chunk_index = last_saved_index  # Resume from the next chunk

    while chunk_index < len(chunks):
        chunk = chunks[chunk_index]

        print("\n" + "=" * 80)
        print(f"📜 Chunk #{chunk_index + 1}")
        print("-" * 80)
        print(chunk["text"])
        print("=" * 80)

        # Get user selection of headers, starting from the last used section
        selected_indices = get_user_selection(headers, last_selected_index)

        if selected_indices == "undo":
            if classified_chunks:
                last_selected_index = classified_chunks[-1]["metadata"].get("last_selected_index", 0)
                classified_chunks.pop()
                chunk_index -= 1
                print("\n🔄 **Undo successful! Returning to previous chunk...**")
            else:
                print("❌ No previous chunk to undo!")
            continue

        if selected_indices == "save":
            save_chunks(output_file, classified_chunks)
            print("\n💾 **Progress saved! You can resume later.**")
            return  # Exit safely

        selected_headers = [headers[i] for i in selected_indices]

        # Add selected headers to the chunk
        chunk["metadata"]["section"] = selected_headers
        chunk["metadata"]["last_selected_index"] = max(selected_indices) if selected_indices else last_selected_index
        classified_chunks.append(chunk)

        # Save progress after each classification
        save_chunks(output_file, classified_chunks)

        # Update for next chunk
        last_selected_index = chunk["metadata"]["last_selected_index"]
        chunk_index += 1

    print("\n🎉 **All chunks classified successfully!**")

# File paths
chunk_file = "catalog.json"  # JSON file containing chunks
header_file = "toc_headers.txt"  # Text file with TOC headers
output_file = "classified_catalog.json"

# Run classification process
classify_chunks(chunk_file, header_file, output_file)
