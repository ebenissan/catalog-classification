import json
import os
import openai

# OpenAI API Client
client = openai.OpenAI()

def generate_section_summary(sections):
    """
    Calls OpenAI API to generate a concise summary of the sections.
    """
    prompt = f"""Given the following list of section titles, summarize them in a concise format while preserving all key details. 
    Structure the summary as follows:
    - Start with the highest-level category (e.g., "Undergraduate Programs of Study").
    - Follow with the specific field or department (if applicable).
    - Include all subsections in parentheses, separated by commas.
    - Ensure the format remains concise and factual, without assumptions or extra details.

    **Example Input:**
    Undergraduate Programs of Study, Mathematics, Minor in Mathematics; 
    Undergraduate Programs of Study, Mathematics, Licensure for Teaching; 
    Undergraduate Programs of Study, Mathematics, Calculus; 
    Undergraduate Programs of Study, Mechanical Engineering

    **Example Output:**
    Undergraduate Programs of Study: Mathematics (Minor in Mathematics, Licensure for Teaching, Calculus) and Mechanical Engineering.

    Now, generate the structured summary for the following section titles:
    {'; '.join(sections)}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that formats section titles into structured summaries."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def save_chunk(output_file, chunk):
    """
    Saves a newly processed chunk progressively by appending it to the output file.
    """
    if os.path.exists(output_file):
        with open(output_file, "r+", encoding="utf-8") as f:
            try:
                classified_chunks = json.load(f)
            except json.JSONDecodeError:
                classified_chunks = []
            classified_chunks.append(chunk)
            f.seek(0)  # Move to start of file
            json.dump(classified_chunks, f, indent=2, ensure_ascii=False)
            f.truncate()  # Remove any leftover data
    else:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump([chunk], f, indent=2, ensure_ascii=False)

    print(f"Progress saved: Chunk #{chunk['metadata']['chunk_number']} added to {output_file}")

def get_last_saved_index(output_file):
    """
    Determines the last processed chunk index to resume from.
    """
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                classified_chunks = json.load(f)
                if classified_chunks:
                    return len(classified_chunks)  # Resume from the next chunk
            except json.JSONDecodeError:
                return 0
    return 0  # Start from the beginning

def process_chunks(input_file, output_file):
    """
    Reads chunks from input JSON, generates summaries progressively, updates text, and saves each processed chunk immediately.
    """
    with open(input_file, "r", encoding="utf-8") as infile:
        chunks = json.load(infile)

    last_saved_index = get_last_saved_index(output_file)

    for i, chunk in enumerate(chunks[last_saved_index:], start=last_saved_index):
        metadata = chunk.get("metadata", {})
        sections = metadata.get("sections", [])
        if sections:
            # Generate section summary using OpenAI
            summary = generate_section_summary(sections)
            # Prepend summary and a separator (two newlines) to the chunk's text
            chunk["text"] = f"{summary}\n\n{chunk['text']}"
        
        chunk["metadata"]["chunk_number"] = i + 1  # Ensure chunk number is accurate
        save_chunk(output_file, chunk)  # Save each chunk progressively

    print(f"\nAll chunks processed and saved in {output_file}")

if __name__ == "__main__":
    input_file = "classified_catalog_agent_new.json"  # Input file containing the original chunks
    output_file = "catalog_english_headers.json"  # Output file for updated chunks
    process_chunks(input_file, output_file)
