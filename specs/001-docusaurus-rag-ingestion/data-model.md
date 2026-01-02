# Data Model: Docusaurus RAG Vector Ingestion Pipeline

## Core Entities

### Document
- **url**: String - Source URL of the crawled page
- **title**: String - Title of the document extracted from HTML
- **section**: String - Section or category the document belongs to
- **content**: String - Clean extracted text content
- **content_hash**: String - Hash of content for duplicate detection
- **created_at**: DateTime - Timestamp when document was first processed
- **updated_at**: DateTime - Timestamp when document was last updated

### TextChunk
- **id**: String - Unique identifier for the chunk
- **document_id**: String - Reference to parent document
- **content**: String - Text content of the chunk (for embedding)
- **chunk_index**: Integer - Position of chunk within document
- **metadata**: Object - Additional metadata including URL, title, section
- **embedding**: Array - Vector embedding from Cohere API
- **created_at**: DateTime - Timestamp when chunk was processed

### CrawlResult
- **url**: String - URL that was crawled
- **status_code**: Integer - HTTP status code of the response
- **content_type**: String - MIME type of the response
- **content_length**: Integer - Size of the content in bytes
- **crawled_at**: DateTime - Timestamp when crawling occurred
- **success**: Boolean - Whether crawling was successful
- **error_message**: String - Error message if crawling failed

## Relationships

### Document-TextChunk Relationship
- One document contains many text chunks (1 to many)
- Each text chunk belongs to exactly one document
- When document is updated, related chunks are updated or recreated
- Document ID is stored as reference in each chunk's metadata

### CrawlResult-Document Relationship
- One crawl result may result in one document (1 to 1 for successful crawls)
- Failed crawl results do not create documents
- Crawl results are used for tracking and debugging purposes

## State Transitions

### Document States
1. **Discovered**: URL found during crawling but not yet processed
2. **Crawled**: Content successfully retrieved from URL
3. **Extracted**: Clean text content extracted from HTML
4. **Chunked**: Content divided into processable chunks
5. **Embedded**: Embeddings generated for all chunks
6. **Stored**: All chunks stored in Qdrant with metadata
7. **Indexed**: Ready for RAG retrieval (final state)

### Processing States
1. **Pending**: Document queued for processing
2. **Processing**: Currently being processed by pipeline
3. **Completed**: Successfully processed and stored
4. **Failed**: Processing failed (with error details)

## Validation Rules

### Content Validation
- Document URL must be a valid, accessible URL
- Content must be non-empty after cleaning
- Content must be below Cohere token limits for single processing
- Title must be extracted from document
- Section information must be determined from URL or content structure

### Chunking Validation
- Each chunk must be between 100 and 1000 words (approximate)
- Chunks must not exceed Cohere's token limit
- Adjacent chunks should have appropriate overlap to preserve context
- Chunk boundaries should respect sentence/paragraph boundaries when possible

### Metadata Validation
- URL must be present and valid
- Title must be present
- Section information must be present
- Document hash must be calculated for duplicate detection
- Timestamps must be accurate

### Embedding Validation
- Embeddings must have consistent dimensions across all chunks
- Embedding generation must succeed without errors
- Embedding vectors must be stored in appropriate format
- Metadata must be preserved alongside embeddings in Qdrant

## Storage Schema

### Qdrant Collection: "rag_embeddings"
- **Point ID**: String - Unique identifier for each chunk
- **Vector**: Array<float> - Embedding vector from Cohere
- **Payload**: Object containing:
  - url: Source URL of the document
  - title: Document title
  - section: Document section or category
  - content: Original chunk content (for context)
  - chunk_index: Position within original document
  - document_hash: Hash of original document
  - created_at: Timestamp of processing
  - updated_at: Timestamp of last update