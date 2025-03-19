import json
import os
import openai

client = openai.OpenAI()

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

# Find the last saved chunk index
def get_last_saved_index(output_file):
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            classified_chunks = json.load(f)
            if classified_chunks:
                last_used_header_index = classified_chunks[-1]["metadata"].get("last_used_header_index", 0)
                return len(classified_chunks), last_used_header_index  # Resume from next chunk
    return 0, 0  # Start from the beginning

# Classify a chunk using GPT while maintaining chronological TOC headers
import re

def classify_with_gpt(chunk_text, headers):
    """
    Uses GPT to classify a text chunk into one or more headers, starting from the given index.
    Expects GPT to return numbers corresponding to header indices. 
    If the response is invalid, it retries until a proper format is received.
    """
    while True:  # Keep asking GPT until the response is formatted correctly
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that categorizes text chunks into sections based on a list of ordered headers.\n"
                        "Do not skip headers—select all applicable headers in order.\n"
                        "Respond ONLY with numbers (e.g., '1-4' or '1,2,3') corresponding to the selected headers. The headers are chronological so none should be skipped. Look very carefully and if you cannot find a match, choose first header option. This is a last resort.\n"
                        "So you understand the acronyms, A&S = Arts and Sciences, Blair = School of Music, VUSE = Vanderbilt School of Engineering, PBDY = Peabody College of Education and Human Development.\n"
                        "Do NOT include explanations or any additional text."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Here is a section of text:\n{chunk_text}\n\n"
                        f"Which of these categories does this text belong to? Only select headers from this list, in chronological order:\n"
                        + "\n".join([f"[{i+1}] {header}" for i, header in enumerate(headers)])
                        + "\n\nReturn only numbers (e.g., '1-4' or '1,2,3')."
                    )
                }
            ],
            temperature=0.2
        )

        raw_response = response.choices[0].message.content.strip()
        print(f"🔹 GPT Response: {raw_response}")  # Debugging output

        # Extract numbers using regex
        selected_indices = []
        try:
            for part in raw_response.split(","):
                part = part.strip()
                if "-" in part:
                    start, end = map(int, part.split("-"))
                    selected_indices.extend(range(start, end + 1))
                else:
                    selected_indices.append(int(part))

            # Convert to zero-based index and filter out-of-range values
            selected_indices = [i - 1 for i in selected_indices]

            if selected_indices:
                return selected_indices  # Return valid selections
        except ValueError:
            pass  # If parsing fails, retry

        print("⚠️ Invalid format received. Retrying...")  # Keep prompting until the response is valid


# Main function to classify chunks automatically
def classify_chunks_with_llm(chunk_file, header_file, output_file):
    headers = load_headers(header_file)  # Load TOC headers
    chunks = load_chunks(chunk_file)  # Load catalog chunks
    last_saved_index, last_used_header_index = get_last_saved_index(output_file)  # Resume from last point

    # If progress exists, load classified chunks; otherwise, start fresh
    classified_chunks = []
    if last_saved_index > 0:
        with open(output_file, "r", encoding="utf-8") as f:
            classified_chunks = json.load(f)

    chunk_index = last_saved_index  # Resume from the next chunk


    while chunk_index < len(chunks):
        chunk = chunks[chunk_index]
        chunk_text = chunk["text"]

        print(f"\n🔹 Classifying Chunk #{chunk_index + 1}/{len(chunks)}...")
    
        headers_list = headers[last_used_header_index:last_used_header_index+10]


        # Ask GPT to select multiple headers, keeping chronological order
        selected_indices = classify_with_gpt(chunk_text, headers_list)

        # Adjust indices to reflect actual header positions
        selected_indices = [i + last_used_header_index for i in selected_indices]  
        selected_headers = [headers[i] for i in selected_indices]


        if not selected_headers:
            print("⚠️ No headers selected. Skipping this chunk.")
        else:
            print(f"✅ Assigned to sections: {selected_headers}")

            # Update the chunk with selected headers
            chunk["metadata"]["sections"] = selected_headers
            # Update the last used header index properly
            last_used_header_index = max(selected_indices) if selected_indices else last_used_header_index

            chunk["metadata"]["last_used_header_index"] = last_used_header_index
            chunk["metadata"]["chunk_number"] = chunk_index + 1


            classified_chunks.append(chunk)

            # Save progress after each classification
            save_chunks(output_file, classified_chunks)

        chunk_index += 1

    print("\n🎉 **All chunks classified successfully!**")

# File paths
chunk_file = "catalog.json"  # JSON file containing chunks
header_file = "toc_headers.txt"  # Text file with TOC headers
output_file = "classified_catalog_agent.json"

# Run classification process
classify_chunks_with_llm(chunk_file, header_file, output_file)
