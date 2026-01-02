# Data Model: RAG Agent Service with OpenAI Agents SDK and FastAPI

## Core Entities

### QuestionRequest
- **question**: String - The user's question text
- **user_id**: String (optional) - Identifier for the user (for tracking purposes)
- **session_id**: String (optional) - Session identifier for conversation context
- **metadata**: Object (optional) - Additional metadata for the request
- **timestamp**: DateTime - When the request was made

### QuestionResponse
- **answer**: String - The agent's answer to the question
- **question**: String - The original question for reference
- **retrieved_chunks**: Array - List of content chunks used to generate the answer
- **confidence_score**: Float - Confidence level in the answer (0.0-1.0)
- **sources**: Array - List of sources cited in the answer
- **timestamp**: DateTime - When the response was generated
- **request_id**: String - Reference to the original request

### RetrievedChunk
- **id**: String - Unique identifier from Qdrant
- **content**: String - Original chunk content from Qdrant
- **similarity_score**: Float - Similarity score from vector search
- **metadata**: Object - Original metadata from Qdrant (URL, title, section, etc.)
- **relevance_score**: Float - Score of relevance to the question (0.0-1.0)
- **used_in_response**: Boolean - Whether this chunk was used in the final response

### AgentContext
- **question**: String - The original user question
- **retrieved_content**: Array - All retrieved content chunks with metadata
- **formatted_context**: String - Context formatted for agent consumption
- **context_tokens**: Integer - Number of tokens in the formatted context
- **retrieval_timestamp**: DateTime - When content was retrieved
- **context_valid**: Boolean - Whether the context is valid for agent use

### AgentResponse
- **raw_response**: String - Raw response from the OpenAI agent
- **processed_answer**: String - Answer after processing and formatting
- **used_context_chunks**: Array - IDs of chunks that were used in the response
- **agent_thoughts**: String (optional) - Internal reasoning from the agent
- **processing_time**: Float - Time taken to generate the response (seconds)
- **response_tokens**: Integer - Number of tokens in the response
- **completion_tokens**: Integer - Number of tokens used for completion

### AgentConfiguration
- **assistant_id**: String - OpenAI assistant ID
- **model**: String - OpenAI model to use (e.g., gpt-4, gpt-3.5-turbo)
- **temperature**: Float - Temperature setting for response creativity
- **max_tokens**: Integer - Maximum tokens for agent responses
- **retrieval_threshold**: Float - Minimum similarity score for retrieved content
- **max_context_chunks**: Integer - Maximum number of chunks to include in context

### APIError
- **error_code**: String - Standardized error code
- **message**: String - Human-readable error message
- **details**: Object (optional) - Additional error details
- **timestamp**: DateTime - When the error occurred
- **request_id**: String - Reference to the request that caused the error

## Relationships

### QuestionRequest-AgentResponse Relationship
- One question request generates one agent response (1 to 1)
- Each agent response belongs to exactly one question request
- Request ID is stored as reference in each agent response

### AgentResponse-RetrievedChunk Relationship
- One agent response may reference multiple retrieved chunks (1 to many)
- Each retrieved chunk may be referenced by multiple responses (many to many)
- Agent response contains array of chunk IDs used in the response

### AgentContext-RetrievedChunk Relationship
- One agent context contains multiple retrieved chunks (1 to many)
- Each retrieved chunk belongs to exactly one agent context during processing
- Context contains array of retrieved chunks with relevance scores

## State Transitions

### Request Processing States
1. **Received**: Question request received by API endpoint
2. **Validating**: Request parameters being validated
3. **Retrieving**: Content being retrieved from Qdrant
4. **ContextBuilding**: Retrieved content being formatted for agent
5. **AgentProcessing**: OpenAI agent generating response
6. **Formatting**: Response being formatted for user delivery
7. **Completed**: Response ready for delivery
8. **Failed**: Processing failed (with error details)

### Agent Orchestration States
1. **Initializing**: Agent configuration being loaded
2. **Ready**: Agent ready to process requests
3. **Processing**: Agent currently handling a request
4. **Waiting**: Agent waiting for external resources (retrieval, API calls)
5. **Completed**: Agent finished processing
6. **Error**: Agent encountered an error

## Validation Rules

### QuestionRequest Validation
- Question must be non-empty and at least 3 characters long
- Question must not exceed token limits for processing
- User ID and session ID must follow proper format if provided
- Request must include all required fields

### RetrievedChunk Validation
- Chunk must have valid similarity score between 0 and 1
- Content must be non-empty and properly formatted
- Metadata must contain required fields (URL, title, section)
- Chunk ID must match the expected format from Qdrant

### AgentResponse Validation
- Answer must be non-empty and properly formatted
- Used context chunks must exist and be valid
- Processing time must be positive
- Response must not exceed token limits

### AgentConfiguration Validation
- Assistant ID must be valid and accessible
- Model must be supported by OpenAI API
- Temperature must be between 0 and 2
- Max tokens must be positive and within API limits
- Retrieval threshold must be between 0 and 1
- Max context chunks must be positive

## Storage Schema

### Qdrant Collection: "rag_embeddings" (existing from previous features)
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

### API Request/Response Schema
- **Request endpoint**: POST /api/v1/ask
- **Request body**: QuestionRequest object
- **Response body**: QuestionResponse object
- **Error responses**: APIError object with appropriate status codes