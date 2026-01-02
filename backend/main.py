import os
import requests
from bs4 import BeautifulSoup
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import time
import hashlib
from typing import List, Dict, Any
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is required")
co = cohere.Client(cohere_api_key)

# Initialize Qdrant client
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
if not qdrant_url or not qdrant_api_key:
    raise ValueError("QDRANT_URL and QDRANT_API_KEY environment variables are required")
qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
)

def get_all_urls(base_url: str) -> List[str]:
    """
    Crawl the Docusaurus site to discover all accessible URLs.

    Args:
        base_url: The base URL of the Docusaurus site

    Returns:
        List of discovered URLs
    """
    urls = set()
    visited = set()
    to_visit = [base_url]

    # Add common Docusaurus documentation paths
    docs_url = base_url.rstrip('/') + '/docs'
    to_visit.append(docs_url)

    while to_visit:
        current_url = to_visit.pop(0)

        if current_url in visited or not current_url.startswith(base_url):
            continue

        visited.add(current_url)
        logger.info(f"Crawling: {current_url}")

        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()

            # Only process HTML content
            if 'text/html' in response.headers.get('content-type', ''):
                urls.add(current_url)

                # Parse the page for more links
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all links that point to other pages
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(current_url, href)

                    # Only add URLs that are part of the same site and haven't been visited
                    if full_url.startswith(base_url) and full_url not in visited:
                        # Filter out external links and special URLs
                        parsed = urlparse(full_url)
                        if parsed.netloc == urlparse(base_url).netloc:
                            to_visit.append(full_url)

            # Be respectful with rate limiting
            time.sleep(0.5)

        except requests.RequestException as e:
            logger.error(f"Error crawling {current_url}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error crawling {current_url}: {e}")
            continue

    return list(urls)

def extract_text_from_url(url: str) -> Dict[str, Any]:
    """
    Extract clean text content from a URL.

    Args:
        url: The URL to extract content from

    Returns:
        Dictionary containing title, content, and section information
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Try to find the main content area
        # Docusaurus typically uses main or specific content containers
        content_selectors = [
            'main',
            '[role="main"]',
            '.main-wrapper',
            '.container',
            '.theme-doc-markdown',
            '.markdown',
            'article',
            '.docs-content',
            '.content'
        ]

        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break

        if not content_element:
            # If no specific content area found, use body
            content_element = soup.find('body')

        if content_element:
            # Extract text, removing extra whitespace
            content = ' '.join(content_element.get_text().split())
        else:
            # Fallback to full body text
            content = ' '.join(soup.get_text().split())

        # Extract title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else "Untitled"

        # Extract section from URL path
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        section = path_parts[0] if path_parts and path_parts[0] else "home"

        return {
            'url': url,
            'title': title,
            'content': content,
            'section': section
        }

    except requests.RequestException as e:
        logger.error(f"Error extracting content from {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error extracting content from {url}: {e}")
        return None

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for RAG-optimized retrieval.

    Args:
        text: The text to chunk
        chunk_size: Size of each chunk (approximate word count)
        overlap: Number of words to overlap between chunks

    Returns:
        List of text chunks
    """
    if not text:
        return []

    # Split text into words
    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)

        # Move start forward by chunk_size minus overlap
        start = end - overlap

        # If we're near the end, make sure we don't go over
        if start >= len(words):
            break

    return chunks

def embed(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Cohere.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    if not texts:
        return []

    # Cohere has limits on batch size, so we'll process in chunks if needed
    embeddings = []

    # Process in batches of up to 96 texts (Cohere's limit)
    batch_size = 96
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        try:
            response = co.embed(
                texts=batch,
                model="embed-english-v3.0",  # Using a reliable Cohere embedding model
                input_type="search_document"  # Optimize for search/document retrieval
            )

            embeddings.extend(response.embeddings)

            # Be respectful with rate limits
            time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            # Return empty embeddings for failed batch
            embeddings.extend([[] for _ in range(len(batch))])

    return embeddings

def create_collection(collection_name: str = "rag_embeddings"):
    """
    Create or connect to a Qdrant collection for storing embeddings.

    Args:
        collection_name: Name of the collection to create/use
    """
    try:
        # Check if collection already exists
        collections = qdrant_client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if collection_name not in collection_names:
            # Create new collection
            # Using Cohere's embedding dimension (typically 1024 for embed-english-v3.0)
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
            )
            logger.info(f"Created new collection: {collection_name}")
        else:
            logger.info(f"Using existing collection: {collection_name}")

        # Set up the collection name as a global or return it for use
        return collection_name

    except Exception as e:
        logger.error(f"Error creating collection {collection_name}: {e}")
        raise

def save_chunk_to_qdrant(chunk_data: Dict[str, Any], embedding: List[float], collection_name: str = "rag_embeddings"):
    """
    Save a text chunk and its embedding to Qdrant with metadata.

    Args:
        chunk_data: Dictionary containing url, title, content, section, etc.
        embedding: The embedding vector
        collection_name: Name of the collection to save to
    """
    try:
        # Create a unique ID for this chunk
        content_hash = hashlib.md5(f"{chunk_data['url']}_{chunk_data['content']}".encode()).hexdigest()

        # Prepare the payload with metadata
        payload = {
            "url": chunk_data['url'],
            "title": chunk_data['title'],
            "section": chunk_data['section'],
            "content": chunk_data['content'],
            "chunk_index": chunk_data.get('chunk_index', 0),
            "document_hash": chunk_data.get('document_hash', ''),
            "created_at": chunk_data.get('created_at', time.time())
        }

        # Upsert the point into Qdrant
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=content_hash,
                    vector=embedding,
                    payload=payload
                )
            ]
        )

        logger.info(f"Saved chunk to Qdrant: {chunk_data['url']}")

    except Exception as e:
        logger.error(f"Error saving chunk to Qdrant: {e}")
        raise

def main():
    """
    Main function to execute the complete RAG ingestion pipeline.
    """
    logger.info("Starting Docusaurus RAG ingestion pipeline...")

    # Get the base URL from environment or use default
    base_url = os.getenv("DOCS_URL", "http://localhost:3000/")
    logger.info(f"Using base URL: {base_url}")

    # Create the collection
    collection_name = create_collection("rag_embeddings")

    # Step 1: Get all URLs from the Docusaurus site
    logger.info("Discovering URLs...")
    urls = get_all_urls(base_url)
    logger.info(f"Discovered {len(urls)} URLs")

    # Process each URL
    for i, url in enumerate(urls):
        logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")

        # Step 2: Extract text content from URL
        content_data = extract_text_from_url(url)
        if not content_data:
            logger.warning(f"Failed to extract content from {url}")
            continue

        # Create document hash for duplicate detection
        doc_hash = hashlib.md5(content_data['content'].encode()).hexdigest()
        content_data['document_hash'] = doc_hash

        # Step 3: Chunk the content
        chunks = chunk_text(content_data['content'])
        logger.info(f"Created {len(chunks)} chunks from {url}")

        # Process each chunk
        for chunk_idx, chunk in enumerate(chunks):
            # Prepare chunk data with index
            chunk_data = content_data.copy()
            chunk_data['content'] = chunk
            chunk_data['chunk_index'] = chunk_idx

            # Step 4: Generate embedding for the chunk
            try:
                embeddings = embed([chunk])
                if embeddings and len(embeddings) > 0 and len(embeddings[0]) > 0:
                    embedding = embeddings[0]

                    # Step 5: Save to Qdrant
                    save_chunk_to_qdrant(chunk_data, embedding, collection_name)
                else:
                    logger.warning(f"Failed to generate embedding for chunk {chunk_idx} of {url}")
                    continue
            except Exception as e:
                logger.error(f"Error processing chunk {chunk_idx} of {url}: {e}")
                continue

    logger.info("Docusaurus RAG ingestion pipeline completed successfully!")

if __name__ == "__main__":
    main()