# Quickstart: RAG Retrieval Pipeline Validation

## Overview
This guide provides instructions for setting up and running the RAG retrieval validation pipeline. The validation system connects to existing Qdrant collections from Spec-1, executes semantic similarity queries, validates retrieved chunks and metadata, and provides comprehensive validation reports.

## Prerequisites
- Python 3.11 or higher
- uv package manager
- Cohere API key (same as used in Spec-1)
- Qdrant Cloud API key and URL (same as used in Spec-1)
- Access to the existing "rag_embeddings" collection from Spec-1
- Previously ingested embeddings in Qdrant (from Spec-1 pipeline)

## Setup Instructions

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Install Dependencies (if not already installed from Spec-1)
```bash
uv add python-dotenv cohere qdrant-client
```

### 3. Update Environment File
Update your existing `.env` file with the following content:
```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
# Collection name from Spec-1
QDRANT_COLLECTION_NAME=rag_embeddings
```

## Validation Functions Overview

The validation.py file will contain these key functions:

### `connect_to_qdrant()`
- Establishes connection to existing Qdrant collection
- Validates connection and collection existence
- Handles authentication and connection errors

### `validate_query_text(query_text)`
- Validates input query before processing
- Checks query quality and format
- Returns validation status and recommendations

### `embed_query(query_text)`
- Converts query text to embedding vector using Cohere
- Ensures embedding matches dimensions of stored vectors
- Handles API rate limits and errors

### `execute_similarity_search(query_embedding, limit=10)`
- Performs vector similarity search against Qdrant collection
- Retrieves top N most similar chunks with metadata
- Returns similarity scores and complete metadata

### `validate_retrieved_chunks(chunks)`
- Verifies metadata completeness and integrity
- Checks content quality and formatting
- Identifies any validation issues

### `assess_relevance(query_text, retrieved_chunks)`
- Evaluates relevance of retrieved results to query
- Calculates relevance scores and confidence metrics
- Provides assessment of content matching

### `generate_validation_report(results)`
- Aggregates validation results into comprehensive report
- Calculates success metrics and statistics
- Provides actionable insights for pipeline improvements

## Running the Validation

### 1. Execute the Validation Function
```bash
python validation.py --query "your query text here"
```

### 2. Or run batch validation
```bash
python validation.py --batch
```

### 3. Monitor the Process
- The validation will connect to Qdrant and execute similarity searches
- Retrieved chunks and metadata will be validated
- Relevance will be assessed and reported
- Final validation report will be generated

### 4. Review Results
- Check validation report for success metrics
- Verify metadata completeness (should be 100%)
- Review relevance scores (should be above 0.7 average)
- Examine any validation issues found

## Configuration Options

### Environment Variables
- `COHERE_API_KEY`: Your Cohere API key (same as Spec-1)
- `QDRANT_API_KEY`: Your Qdrant Cloud API key (same as Spec-1)
- `QDRANT_URL`: Your Qdrant Cloud cluster URL (same as Spec-1)
- `QDRANT_COLLECTION_NAME`: Name of collection to validate (default: rag_embeddings)
- `VALIDATION_LIMIT`: Number of results to retrieve per query (default: 10)
- `RELEVANCE_THRESHOLD`: Minimum relevance score (default: 0.7)

### Command Line Options
- `--query`: Single query to validate
- `--batch`: Run batch validation with multiple test queries
- `--limit`: Number of results to retrieve per query
- `--output`: Output file for validation report

## Troubleshooting

### Common Issues
- API rate limits: The validation includes built-in delays to respect rate limits
- Network timeouts: The validation has retry mechanisms for network issues
- Invalid queries: The system validates queries before processing
- Qdrant connection issues: The system validates connection before proceeding

### Logging
- All validation operations are logged for debugging and monitoring
- Error messages provide specific details for troubleshooting
- Validation reports include comprehensive statistics for analysis

## Validation Metrics

### Success Criteria
- Metadata completeness: 100% of retrieved chunks have complete metadata
- Relevance score: Average above 0.7 across all queries
- Query validation accuracy: 95% accuracy in query validation
- Performance: Validation completes within 30 seconds
- Edge case handling: Proper responses for no results, empty collections, etc.