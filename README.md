# Chunk Classification Tool README

This tool helps you classify text chunks into hierarchical sections based on a table of contents. It allows you to review text chunks one by one and assign them to the appropriate section(s) from a predefined list of headers.

## Requirements

This script requires Python 3.6 or higher.

## Setup

1. Clone or download this repository to your local machine.

2. Create and activate a virtual environment:

   **On macOS/Linux:**
   ```
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Input Files

The tool requires two input files:

1. `toc_headers.txt`: A text file containing hierarchical headers, one per line
2. `catalog.json`: A JSON file containing chunks of text to classify

## Usage

1. Make sure your input files are in the correct format and location.

2. Run the script:
   ```
   python classify_chunks.py
   ```

3. For each chunk of text displayed:
   - Review the content
   - Select appropriate section(s) by entering numbers, ranges (e.g., "2-4"), or comma-separated values (e.g., "1,3,5")
   - Type "undo" to go back to the previous chunk if you make a mistake

4. The tool will save your progress after each classification to `classified_catalog.json`.

## Features

- Displays chunks one at a time for review
- Shows only 10 header options at a time for easier navigation
- Allows selection of multiple headers per chunk
- Supports undo functionality to correct mistakes
- Saves progress after each classification
- Provides clear visual separation between chunks

## Output

The classified chunks will be saved to `classified_catalog.json` with the selected section headers added to each chunk's metadata.

## Customization

You can modify the file paths in the script if needed:
- `chunk_file`: Path to the JSON file containing chunks
- `header_file`: Path to the text file with TOC headers
- `output_file`: Path to save the classified chunks

## Note

This tool is designed to help you efficiently categorize large amounts of text into a structured hierarchy, making it easier to organize and navigate content.