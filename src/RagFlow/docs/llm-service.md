# LLM Service Documentation

## Overview

`LLMService` is a service class that acts as a wrapper around an LLM client (specifically `OpenAPIClient`) to simplify interactions with a language model API. It also includes a factory function (`llm_service_factory`) to instantiate the service with a pre-configured OpenAI client. The code abstracts away the details of the LLM client, making it easy to generate text predictions or embeddings based on user input.

The file consists of two main components:

1. `LLMService`: A class that provides high-level methods for text prediction and embeddings
2. `llm_service_factory`: A function that creates an instance of `LLMService` with a default OpenAI client

## LLMService

### Purpose
`LLMService` is a service class that encapsulates an `LLMClientInterface` implementation (e.g., `OpenAPIClient`) and provides a simplified interface for interacting with a language model. It handles the construction of message payloads and delegates the actual API calls to the underlying client.

### Initialization

#### Constructor: `LLMService(llm_client: LLMClientInterface)`
- **Parameters**:
  - `llm_client`: An instance of a class implementing `LLMClientInterface` (e.g., `OpenAPIClient`)
- **Attributes**:
  - `self.llm_client`: Stores the provided LLM client for subsequent method calls

### Methods

#### `predict(user_prompt: str)`
- **Purpose**: Generates a text response based on a user-provided prompt by calling the underlying client's `predict()` method
- **Parameters**:
  - `user_prompt`: A string containing the user's input (e.g., "What is the weather like today?")
- **Behavior**:
  - Constructs a message list with two entries:
    - A system message: "You are a helpful assistant." (defines the assistant's role)
    - A user message: The provided `user_prompt`
  - Passes this list to the `llm_client.predict()` method with default parameters (e.g., `temperature=0.7`, `max_tokens=1000` from `OpenAPIClient`)
- **Returns**: The full JSON response from the underlying client (e.g., containing the generated text under choices)

**Example**:
```python
from core.llm.openapi_client import OpenAPIClient
api_key = "your-api-key"
client = OpenAPIClient(api_key)
service = LLMService(client)
response = service.predict("What is Python?")
print(response["choices"][0]["message"]["content"])
# Output: "Python is a high-level, interpreted programming language known for its simplicity and versatility."
```

#### `get_embeddings(input_text: str)`
- **Purpose**: Retrieves embeddings (vector representations) for the provided text by calling the underlying client's `get_embeddings()` method
- **Parameters**:
  - `input_text`: The text to embed (e.g., "Hello, world!")
- **Returns**: A list of embeddings (e.g., `[[0.1, 0.2, ...], ...]`)

**Example**:
```python
service = LLMService(OpenAPIClient("your-api-key"))
embeddings = service.get_embeddings("I love coding!")
print(embeddings[0][:5])  # First 5 values of the first embedding
# Output: [0.0123, -0.0456, 0.0789, -0.0012, 0.0345]
```

## llm_service_factory

### Purpose
`llm_service_factory` is a factory function that creates and returns an instance of `LLMService` pre-configured with an `OpenAPIClient`. It uses configuration values (`OPENAI_API_KEY` and `OPENAI_API_MODEL`) to initialize the client, making it a convenient way to instantiate the service without manually passing parameters.

### Definition
- **Function**: `llm_service_factory() -> LLMService`
- **Behavior**:
  - Creates an `OpenAPIClient` instance using `OPENAI_API_KEY` and `OPENAI_API_MODEL` from `core.common.config`
  - Passes the client to the `LLMService` constructor and returns the resulting service object
- **Returns**: An initialized `LLMService` instance

**Example**:
```python
# Assuming OPENAI_API_KEY and OPENAI_API_MODEL are set in core.common.config
service = llm_service_factory()
response = service.predict("Tell me a joke.")
print(response["choices"][0]["message"]["content"])
# Output: "Why don't skeletons fight each other? Because they don't have the guts."
```

### Key Features
- **Abstraction**: `LLMService` simplifies interaction with the LLM client by predefining the system message and exposing a clean API
- **Dependency Injection**: The service accepts any `LLMClientInterface` implementation, making it flexible for use with different LLM providers
- **Configuration**: The factory function uses centralized configuration values (`OPENAI_API_KEY`, `OPENAI_API_MODEL`), reducing hardcoded dependencies
- **Type Hints**: Uses Python's typing module for better code readability and IDE support

### Dependencies
- `os`: Imported but not used (possibly for future environment variable access)
- `typing`: Provides `List` for type hints
- `core.common.config`: Supplies `OPENAI_API_KEY` and `OPENAI_API_MODEL` constants
- `core.llm.openapi_client`: Provides `LLMClientInterface` and `OpenAPIClient` classes

### Example Usage
```python
# Using the factory function
service = llm_service_factory()

# Generate a text prediction
response = service.predict("What is the capital of Brazil?")
print(response["choices"][0]["message"]["content"])
# Output: "The capital of Brazil is Brasília."

# Get embeddings for a sentence
embeddings = service.get_embeddings("I enjoy learning new things.")
print(len(embeddings[0]))  # Length of the embedding vector
# Output: 1536 (typical embedding size for text-embedding-ada-002)
```

### Notes
- The `predict()` method returns the full JSON response from the OpenAI API. To extract the generated text, use `response["choices"][0]["message"]["content"]`
- The system message "You are a helpful assistant." is hardcoded, but it could be made configurable by adding a parameter to `__init__`
- Ensure that `OPENAI_API_KEY` and `OPENAI_API_MODEL` are properly defined in `core.common.config` before calling `llm_service_factory()`

```mermaid
+-------------------+       +-------------------+       +-------------------+
| LLMClientInterface|       |   OpenAPIClient   |       |     LLMService    |
| (Abstract Class)  |       | (Concrete Class)  |       |    (Service Layer)|
+-------------------+       +-------------------+       +-------------------+
| - predict()       |<----->| - predict()       |<----->| - predict()       |
| - get_embeddings()|       | - get_embeddings()|       | - get_embeddings()|
+-------------------+       +-------------------+       +-------------------+
                            | - api_key         |       | - llm_client      |
                            | - model           |       +-------------------+
                            | - base_url        |
                            | - headers         |
                            +-------------------+
                                    ^
                                    |
                                    |
                            +-------------------+
                            | llm_service_factory|
                            |    (Function)     |
                            +-------------------+
                            | Creates OpenAPIClient with: |
                            | - OPENAI_API_KEY  |
                            | - OPENAI_API_MODEL|
                            +-------------------+
                                    |
                                    v
                            +-------------------+
                            |     LLMService    |
                            |   (Instantiated)  |
                            +-------------------+

```