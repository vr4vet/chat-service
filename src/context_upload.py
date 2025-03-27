import os
import uuid
import logging

# Import your project modules.
from src.config import Config
from src.rag_service.context import Context
from src.rag_service.embeddings import create_embeddings_model
from src.rag_service.dao import get_database

# Load configuration and initialize the SentenceTransformer model.
config = Config()
embedding_model = create_embeddings_model()

def compute_embedding(text: str) -> list[float]:
    """
    Computes an embedding for the given text using a SentenceTransformer model.

    Args:
        text (str): The text to embed.

    Returns:
        list[float]: The computed embedding as a list of floats.
    """
    embeddings = embedding_model.get_embedding(text)
    return embeddings

def process_file_and_store(file_path: str, NPC: int) -> bool:
    """
    Processes a .txt or .md file, extracts its text, computes its embedding, and
    stores the data in the database.

    Args:
        file_path (str): Path to the text or markdown file.
        NPC (int): NPC identifier to associate with this context.

    Returns:
        bool: True if storing was successful; False otherwise.
    """
    logging.info(f"Starting file processing for: {file_path} with NPC: {NPC}")

    # Verify file exists
    if not os.path.exists(file_path):
        logging.error(f"File '{file_path}' does not exist.")
        return False

    # Verify file extension is supported
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in ['.txt', '.md']:
        logging.error("Unsupported file type. Only .txt and .md files are supported.")
        return False

    # Attempt to read the file with UTF-8, then fallback to CP-1252 (Windows-1252)
    used_encoding = None
    file_content = None

    # 1) Try UTF-8
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        used_encoding = 'utf-8'
    except UnicodeDecodeError as e_utf8:
        logging.warning(
            f"Failed to decode '{file_path}' as UTF-8. Will attempt Windows-1252. "
            f"Error: {e_utf8}"
        )

    # 2) Fallback to CP-1252 if UTF-8 failed
    if file_content is None:
        try:
            with open(file_path, 'r', encoding='cp1252') as f:
                file_content = f.read()
            used_encoding = 'cp1252'
        except UnicodeDecodeError as e_cp1252:
            error_msg = (
                f"Failed to decode '{file_path}' with both UTF-8 and CP-1252. "
                f"These are the only encodings we support. Error details:\n"
                f"- UTF-8 error: {e_utf8}\n"
                f"- CP-1252 error: {e_cp1252}"
            )
            logging.error(error_msg)
            return False

    # If we reach here, we read the file successfully with either utf-8 or cp1252
    logging.info(
        f"Successfully read file '{file_path}' using '{used_encoding}' encoding."
    )

    # Compute the embedding
    try:
        embedding = compute_embedding(file_content)
    except Exception as e:
        logging.error(f"Error computing embedding for file '{file_path}': {e}")
        return False

    # Use the file's basename as the document name
    document_name = os.path.basename(file_path)

    # Generate a unique document ID
    document_id = str(uuid.uuid4())

    # Get the configured database instance
    db = get_database()

    try:
        success = db.post_context(
            text=file_content,
            NPC=NPC,
            embedding=embedding,
            document_id=document_id,
            document_name=document_name
        )
    except Exception as e:
        logging.error(f"Error posting context to the database: {e}")
        return False

    if success:
        logging.info(
            f"Successfully stored '{document_name}' in the database "
            f"(read as {used_encoding})."
        )
    else:
        logging.error(f"Failed to store '{document_name}' in the database.")

    return success

if __name__ == '__main__':
    file_path = "src.context_files.salmon.txt"
    NPC = 100
    process_file_and_store(file_path, NPC)
