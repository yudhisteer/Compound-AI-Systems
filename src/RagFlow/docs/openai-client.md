# OpenAI Client Documentation

The OpenAPIClient defines an interface and a concrete implementation for interacting with OpenAI's API to perform two key tasks: generating text predictions (e.g., chat completions) and obtaining text embeddings (vector representations of text). The code is designed with modularity, error handling, and retry logic to make it robust for production use.

## Components

The code consists of two main components:

1. `LLMClientInterface`: An abstract base class that defines a standard contract for any language model (LLM) client.
2. `OpenAPIClient`: A concrete implementation of the interface that interacts with OpenAI's API.

## LLMClientInterface

### Purpose
`LLMClientInterface` is an abstract base class that outlines the required methods for any LLM client implementation. It ensures consistency across different LLM providers or models by enforcing the implementation of two core methods: `predict()` for text generation and `get_embeddings()` for generating vector embeddings.

### Methods

#### `predict(messages: List[dict], max_tokens=1000, temperature=0.1)`
- **Purpose**: Generates text based on a list of message dictionaries (e.g., a conversation history).
- **Parameters**:
  - `messages`: A list of dictionaries representing the conversation (e.g., `[{"role": "user", "content": "Hello"}]`)
  - `max_tokens`: Maximum number of tokens to generate (default: 1000)
  - `temperature`: Controls randomness of the output (default: 0.1, low randomness)
- **Raises**: `NotImplementedError` if not overridden

#### `get_embeddings(input_text: str) -> List[list]`
- **Purpose**: Converts input text into a list of numerical embeddings (vectors)
- **Parameters**:
  - `input_text`: The text to embed
- **Returns**: A list of lists (embeddings)
- **Raises**: `NotImplementedError` if not overridden

### Usage
This interface is not used directly but serves as a blueprint for concrete implementations like `OpenAPIClient`.

## OpenAPIClient

### Purpose
`OpenAPIClient` is a concrete implementation of `LLMClientInterface` that interacts with OpenAI's API. It provides methods to generate text predictions and embeddings using OpenAI's models, with built-in error handling and retry logic for robustness.

### Initialization

#### Constructor: `OpenAPIClient(api_key: str, model: str = "gpt-4o-mini")`
- **Parameters**:
  - `api_key`: Your OpenAI API key
  - `model`: The OpenAI model to use for predictions (default: "gpt-4o-mini")
- **Attributes**:
  - `base_url`: The OpenAI API base URL ("https://api.openai.com/v1")
  - `headers`: HTTP headers including the API key and content type

### Methods

#### `predict(messages: List[dict], temperature: float = 0.7, max_tokens: int = 1000) -> str`
- **Purpose**: Sends a list of messages to OpenAI's chat completion endpoint and returns the generated response
- **Parameters**:
  - `messages`: A list of dictionaries (e.g., `[{"role": "user", "content": "What is Python?"}]`)
  - `temperature`: Controls creativity (default: 0.7, moderate randomness)
  - `max_tokens`: Maximum tokens in the response (default: 1000)
- **Behavior**:
  - Makes a POST request to `/chat/completions`
  - Uses the `@retry_with_exponential_backoff` decorator to retry on rate limit (429) or other OpenAI errors
  - Raises `OpenAIRateLimitError` or `OpenAIError` if the request fails
- **Returns**: The full JSON response from OpenAI (e.g., containing the generated text under choices)

**Example**:
```python
client = OpenAPIClient(api_key="your-api-key")
messages = [{"role": "user", "content": "Explain Python in one sentence."}]
response = client.predict(messages)
print(response["choices"][0]["message"]["content"])
```

#### `get_embeddings(input_text: str) -> List[list]`
- **Purpose**: Converts input text into a list of embeddings using OpenAI's embedding endpoint
- **Parameters**:
  - `input_text`: The text to embed (e.g., "Hello, world!")
- **Behavior**:
  - Makes a POST request to `/embeddings` using the "text-embedding-ada-002" model
  - Raises an exception if the request fails
- **Returns**: A list of embeddings (e.g., `[[0.1, 0.2, ...], ...]`)

**Example**:
```python
client = OpenAPIClient(api_key="your-api-key")
embeddings = client.get_embeddings("Hello, world!")
print(embeddings[0][:5])  # First 5 values of the first embedding
# Output: [0.0123, -0.0456, 0.0789, -0.0012, 0.0345]
```

### Key Features
- **Modularity**: The `LLMClientInterface` allows swapping out `OpenAPIClient` for other LLM providers (e.g., Anthropic, Hugging Face) by implementing the same interface
- **Error Handling**: Custom exceptions (`OpenAIError`, `OpenAIRateLimitError`) and retry logic handle API failures gracefully
- **Retry Logic**: The `@retry_with_exponential_backoff` decorator retries requests on rate limits or errors, using configurable `OPENAI_BACKOFF` and `OPENAI_MAX_RETRIES`
- **Type Hints**: Uses Python's typing module for better code clarity and IDE support

### Dependencies
- `requests`: For making HTTP requests to OpenAI's API
- `core.common.config`: Provides `OPENAI_BACKOFF` and `OPENAI_MAX_RETRIES` constants
- `core.common.http_retry`: Provides the `retry_with_exponential_backoff` decorator
- `core.llm.utils`: Provides `OpenAIError` and `OpenAIRateLimitError` exception classes

### Example Usage
```python
# Initialize the client
client = OpenAPIClient(api_key="your-api-key", model="gpt-4o-mini")

# Generate a text prediction
messages = [{"role": "user", "content": "What is the capital of France?"}]
response = client.predict(messages, temperature=0.5, max_tokens=50)
print(response["choices"][0]["message"]["content"])
# Output: "The capital of France is Paris."

# Get embeddings for a sentence
embeddings = client.get_embeddings("I love coding!")
print(len(embeddings[0]))  # Length of the embedding vector
# Output: 1536 (typical embedding size for text-embedding-ada-002)
```

### Notes
- The `predict()` method returns the full JSON response. To extract the generated text, use `response["choices"][0]["message"]["content"]`
- The embedding model is hardcoded to "text-embedding-ada-002", which may differ from the model used for predictions
- Ensure your API key has sufficient permissions and quota for the requested operations