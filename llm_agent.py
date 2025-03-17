import fitz  # PyMuPDF
import hashlib
import json
from dotenv import load_dotenv

def extract_text_from_pdf(pdf_path):
    """Extracts full plaintext from the PDF, page by page."""
    doc = fitz.open(pdf_path)
    text = [page.get_text("text") for page in doc]
    return "\n".join(text)


def extract_toc(pdf_path):
    """Extracts the Table of Contents from the PDF."""
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()
    return [{"title": title, "page": page} for level, title, page in toc]



import re

def chunk_text(text, chunk_size=1000):
    """Splits text into smaller chunks based on word count."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunk_id = hashlib.sha256(chunk.encode()).hexdigest()
        chunks.append({
            "id": chunk_id,
            "text": chunk,
            "metadata": {
                "source": "catalog",
                "chunk_number": len(chunks) + 1
            }
        })
    return chunks


import openai
import getpass
import os

def _set_env_variables():
    load_dotenv()

    # Dictionary of required API keys
    required_keys = {
        "OPENAI_API_KEY": "OpenAI",
    }

    # Check each required key
    for env_var, service_name in required_keys.items():
        if not os.getenv(env_var):
            os.environ[env_var] = getpass.getpass(
                f"Enter API key for {service_name}: "
            )

    return required_keys

def classify_chunk_with_gpt(OPENAI_API_KEY, chunk_text, toc):
    """Uses GPT to determine the correct section title for a given text chunk."""
    prompt = f"""
    You are an AI trained to classify academic text. Given the Table of Contents:

    {json.dumps(toc, indent=2)}

    And the following excerpt:

    "{chunk_text[:1000]}"  # Only send first 1000 characters

    Which section from the TOC does this text belong to? Return only the section title.
    """

    client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Initialize the new client

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an expert at classifying academic text sections."},
                {"role": "user", "content": prompt}]
    )

    section_title = response.choices[0].message.content.strip()

if __name__ == "__main__":

        # Specify PDF path
    pdf_path = "catalog_new.pdf"

    openai_api_key = _set_env_variables()["OPENAI_API_KEY"]

    # Extract the text
    full_text = extract_text_from_pdf(pdf_path)

    # Extract TOC
    toc = extract_toc(pdf_path)

    # Create chunks
    text_chunks = chunk_text(full_text, chunk_size=1000)


    # Loop through chunks and assign section titles
    for chunk in text_chunks:
        chunk["metadata"]["section"] = classify_chunk_with_gpt(openai_api_key, chunk["text"], toc)

    # Save the updated JSON
    output_json_path = "labeled_chunks.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(text_chunks, f, indent=4)

    print(f"Labeled chunks saved to {output_json_path}")
