import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import DOCS_PATH


def parse_metadata(text):
    """
    Extract metadata from the top of the file.
    Format expected:
    MetaData:
    Field1: Value1
    ...
    Text:
    Actual content starts here...
    """
    metadata = {}
    if "MetaData:" in text and "Text:" in text:
        parts = text.split("Text:", 1)
        meta_block = parts[0].replace("MetaData:", "").strip()
        main_text = parts[1].strip()
        
        for line in meta_block.split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip().lower().replace(" ", "_")] = val.strip()
        return metadata, main_text
    return {}, text


def load_documents():
    """Load all .txt hardware guide documents from the data folder."""
    documents = []
    if not os.path.exists(DOCS_PATH):
        print(f"Warning: {DOCS_PATH} directory not found.")
        return documents

    for filename in sorted(os.listdir(DOCS_PATH)):
        if filename.endswith(".txt") or filename.endswith(".md"):
            filepath = os.path.join(DOCS_PATH, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                raw_text = f.read()
            
            file_metadata, clean_text = parse_metadata(raw_text)
            
            # Use Website Name or Title as source_name if available
            source_name = file_metadata.get("website_name") or file_metadata.get("title") or filename.replace(".txt", "").replace(".md", "").replace("_", " ").title()
            
            documents.append({
                "source": source_name,
                "filename": filename,
                "text": clean_text,
                "extra_metadata": file_metadata
            })
    print(f"Loaded {len(documents)} document(s): {[d['source'] for d in documents]}")
    return documents


def chunk_document(text, source_name, filename, extra_metadata):
    """
    Split a document into chunks using RecursiveCharacterTextSplitter.
    """
    chunk_size = 450
    overlap = 100

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        is_separator_regex=False,
    )

    docs = splitter.create_documents([text])
    
    chunks = []
    prefix = filename.lower().replace(" ", "_").replace(".", "_")
    
    for i, doc in enumerate(docs):
        # Approximate line number calculation
        # We search for the chunk text in the original text (which doesn't have metadata block)
        # However, the user wants line numbers from the source.
        # Since we stripped metadata, we need to be careful.
        # Let's assume the line number should be relative to the 'Text:' start or the whole file?
        # Usually, line 1 of the 'Text:' section is preferred if we want to point to content.
        
        start_index = text.find(doc.page_content)
        line_number = text.count("\n", 0, max(0, start_index)) + 1
        
        chunk_meta = {
            "source": source_name,
            "file": filename,
            "line": line_number,
        }
        # Add all extra metadata from the file header
        chunk_meta.update(extra_metadata)
        
        chunks.append({
            "text": doc.page_content,
            "metadata": chunk_meta,
            "chunk_id": f"{prefix}_{i}",
        })

    return chunks
