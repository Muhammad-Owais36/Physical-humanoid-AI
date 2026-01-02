# Data Model: Frontend and Backend Integration for Local RAG Chatbot

## Entities

### Question
- **Description**: User's query submitted to the RAG agent service
- **Fields**:
  - `text` (string): The question text from the user
  - `user_id` (string, optional): Identifier for the user (for tracking purposes)
  - `session_id` (string, optional): Session identifier for conversation context
  - `metadata` (object, optional): Additional metadata for the request
- **Validation**: Text must be 1-2000 characters, session_id must be valid UUID format if provided

### Response
- **Description**: Answer from the RAG agent service
- **Fields**:
  - `answer` (string): The generated answer text
  - `question` (string): The original question text
  - `retrieved_chunks` (array): List of content chunks used to generate the answer
  - `confidence_score` (number): Confidence score between 0 and 1
  - `sources` (array): List of source URLs cited in the response
  - `request_id` (string): Unique identifier for the request
- **Validation**: Answer must not be empty, confidence_score must be between 0 and 1

### RetrievedChunk
- **Description**: Content chunk retrieved from the vector database
- **Fields**:
  - `id` (string): Unique identifier for the chunk
  - `content` (string): The actual content text
  - `similarity_score` (number): Similarity score between 0 and 1
  - `metadata` (object): Metadata including URL, title, section, etc.
  - `relevance_score` (number): Relevance score between 0 and 1
  - `used_in_response` (boolean): Whether the chunk was used in the response
- **Validation**: Content must not be empty, scores must be between 0 and 1

### ChatMessage
- **Description**: A message in the chat conversation
- **Fields**:
  - `id` (string): Unique identifier for the message
  - `role` (string): "user" or "assistant"
  - `content` (string): The message content
  - `timestamp` (string): ISO timestamp of when the message was created
  - `sources` (array, optional): Sources cited in the response (for assistant messages)
- **Validation**: Role must be either "user" or "assistant", content must not be empty

### ChatSession
- **Description**: User's conversation context
- **Fields**:
  - `session_id` (string): Unique identifier for the session
  - `messages` (array): List of chat messages in the session
  - `created_at` (string): ISO timestamp of session creation
  - `last_activity` (string): ISO timestamp of last message
- **Validation**: Session_id must be valid UUID format

## API Request/Response Models

### ChatRequest
- **Purpose**: Request model for chat endpoint
- **Fields**:
  - `message` (string): The user's message/question
  - `session_id` (string, optional): Session identifier for conversation context
  - `user_preferences` (object, optional): User preferences for the response

### ChatResponse
- **Purpose**: Response model for chat endpoint
- **Fields**:
  - `response` (string): The assistant's response
  - `session_id` (string): The session identifier
  - `sources` (array): List of source URLs cited
  - `confidence` (number): Confidence score for the response
  - `timestamp` (string): ISO timestamp of response