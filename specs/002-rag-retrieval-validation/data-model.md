# Data Model: RAG Retrieval Pipeline Validation

## Core Entities

### Query
- **text**: String - The input query text for similarity search
- **embedding**: Array - Vector embedding of the query text (from Cohere)
- **query_hash**: String - Hash of the query for duplicate detection
- **created_at**: DateTime - Timestamp when query was processed
- **validated_at**: DateTime - Timestamp when validation was completed

### ValidationResult
- **query_id**: String - Reference to the original query
- **retrieved_chunks**: Array - List of retrieved text chunks with metadata
- **relevance_score**: Float - Average relevance score of results
- **metadata_completeness**: Float - Percentage of complete metadata fields
- **content_relevance**: Float - Assessment of content relevance to query
- **validation_status**: String - Status of validation (pass, fail, partial)
- **created_at**: DateTime - Timestamp when validation was performed

### RetrievedChunk
- **id**: String - Unique identifier from Qdrant
- **content**: String - Original chunk content from Qdrant
- **similarity_score**: Float - Similarity score from vector search
- **metadata**: Object - Original metadata from Qdrant (URL, title, section, etc.)
- **validation_issues**: Array - List of validation issues found
- **is_valid**: Boolean - Whether this chunk passed validation
- **created_at**: DateTime - Timestamp when chunk was retrieved

### ValidationReport
- **id**: String - Unique identifier for the validation run
- **query_count**: Integer - Number of queries tested
- **success_rate**: Float - Percentage of successful validations
- **avg_relevance_score**: Float - Average relevance across all queries
- **metadata_completeness_rate**: Float - Percentage of complete metadata
- **total_chunks_validated**: Integer - Total number of chunks checked
- **issues_found**: Array - Summary of issues found during validation
- **execution_time**: Float - Time taken to complete validation (seconds)
- **created_at**: DateTime - Timestamp when validation was completed

### QueryValidationResult
- **query**: String - Original query text
- **is_valid**: Boolean - Whether the query is valid for processing
- **validation_errors**: Array - List of validation errors found
- **recommended_action**: String - Suggested action for invalid queries
- **quality_score**: Float - Assessment of query quality (0.0-1.0)
- **created_at**: DateTime - Timestamp when query was validated

## Relationships

### Query-ValidationResult Relationship
- One query generates one validation result (1 to 1)
- Each validation result belongs to exactly one query
- When query is re-validated, a new validation result is created
- Query ID is stored as reference in each validation result

### ValidationResult-RetrievedChunk Relationship
- One validation result contains many retrieved chunks (1 to many)
- Each retrieved chunk belongs to exactly one validation result
- When validation is re-run, new chunks are created for the new result
- Validation result ID is stored as reference in each chunk's metadata

### ValidationReport-ValidationResult Relationship
- One validation report contains many validation results (1 to many)
- Each validation result belongs to exactly one validation report
- Report aggregates results from multiple queries
- Report ID is not stored in results (aggregation relationship)

## State Transitions

### ValidationResult States
1. **Pending**: Query submitted for validation but not yet processed
2. **Processing**: Vector search in progress against Qdrant
3. **Retrieved**: Chunks retrieved from Qdrant but not yet validated
4. **Validated**: All chunks validated and results assessed
5. **Completed**: Validation report generated and finalized
6. **Failed**: Validation failed due to errors (with error details)

### ValidationReport States
1. **Draft**: Report in progress, results being collected
2. **Processing**: Aggregating validation results
3. **Completed**: All validations complete and report finalized
4. **Published**: Report available for review and analysis
5. **Archived**: Report stored for historical reference

## Validation Rules

### Query Validation
- Query text must be non-empty and at least 3 characters long
- Query must not contain only special characters or numbers
- Query should be in a supported language for the Cohere model
- Query should be under Cohere's token limits for embedding

### RetrievedChunk Validation
- Chunk must have a valid similarity score between 0 and 1
- Metadata must contain all required fields (URL, title, section, content)
- Content must be non-empty and properly formatted
- Chunk ID must match the expected format from Qdrant

### ValidationResult Validation
- Relevance score must be between 0 and 1
- Metadata completeness must be between 0 and 1 (percentage)
- Validation status must be one of: pass, fail, partial
- Retrieved chunks must contain at least one valid result

### ValidationReport Validation
- Success rate must be between 0 and 1 (percentage)
- Average relevance score must be between 0 and 1
- Execution time must be positive and under 30 seconds (requirement)
- Query count must be positive
- All referenced validation results must exist

## Storage Schema

### Qdrant Collection: "rag_embeddings" (existing from Spec-1)
- **Point ID**: String - Unique identifier for each chunk
- **Vector**: Array<float> - Embedding vector from Cohere (1024 dimensions)
- **Payload**: Object containing:
  - url: Source URL of the document
  - title: Document title
  - section: Document section or category
  - content: Original chunk content (for context)
  - chunk_index: Position within original document
  - document_hash: Hash of original document
  - created_at: Timestamp of processing
  - updated_at: Timestamp of last update

### Local Validation Results Storage
- **File**: validation_results.json or similar
- **Format**: JSON with validation report structure
- **Contents**: Complete validation results with all details
- **Timestamp**: When validation was completed