
## Tools in Model Context Protocol

### What are tools in MCP?
Tools are nothing more than functions that can be called by the LLM.They are exposed by the server and can be called by the client.These functions provide more capabilties to the LLM beyond just the ones provided by the model itself - peforming calculations, accessing external resources,...

Below we will see how the LLM can `discover` the tools that are available and subsequently how to `call` them when necessary. 

### Creating a tool
In order to create a tool, we need to define the function and decorate it with the `@mcp.tool()` decorator. Let's see an example if a tool which calculates the BMI of a person.

The function takes two arguments: `weight_kg` which is the weight of the person in kilograms (float) and `height_cm` which is the height of the person in centimeters (float). The function returns a `BMIResponse` object.

```python
from mcp.server import mcp
from pydantic import BaseModel, Field

# Define the response model
class BMIResponse(BaseModel):
    bmi: float = Field(..., description="Calculated BMI value", ge=0)
    category: str = Field(..., description="BMI category (Underweight, Normal, Overweight, Obese)")

@mcp.tool()
def calculate_bmi(weight_kg: float = Field(..., description="Weight in kilograms", gt=0),
                 height_cm: float = Field(..., description="Height in centimeters", gt=0)) -> BMIResponse:
    """Calculate BMI given weight in kg and height in centimeters.
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        
        Returns:
          BMIResponse containing:
            - bmi: Calculated BMI value
            - category: BMI category (Underweight, Normal, Overweight, Obese)
    """
    # Convert height from cm to m
    height_m = height_cm / 100

    # Calculate BMI
    bmi = weight_kg / (height_m ** 2)
    
    # Determine BMI category
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 24.9:
        category = "Normal"
    elif bmi < 29.9:
        category = "Overweight"
    else:
        category = "Obese"

    return BMIResponse(bmi=bmi, category=category)
```

And that's it! We have defined a tool that can be called by the LLM. It is as simple as that.

### Tools Structure
The good thing about exposing tools by the servers is that all tools have a `standard` structure. This allows the client to know what to expect from the server in terms of tools and their parameters. Below is the structure of a tool:

```ts
{
  name: string;          // Unique identifier for the tool
  description?: string;  // Human-readable description
  inputSchema: {         // JSON Schema for the tool's parameters
    type: "object",
    properties: { ... }  // Tool-specific parameters
  },
  annotations?: {        // Optional hints about tool behavior
    title?: string;      // Human-readable title for the tool
    readOnlyHint?: boolean;    // If true, the tool does not modify its environment
    destructiveHint?: boolean; // If true, the tool may perform destructive updates
    idempotentHint?: boolean;  // If true, repeated calls with same args have no additional effect
    openWorldHint?: boolean;   // If true, tool interacts with external entities
  }
}
```

So in our case, the tool `calculate_bmi` will have the following structure after we call the `list_tools` method:

```python
# Get list of available tools from the server
tools = await session.list_tools()
tools_dict = [tool.__dict__ for tool in tools.tools]
debug_print("Available tools:", json.dumps(tools_dict, indent=2))
```

The LLM will be exposed to the list of tools and their structure. This is how it will reason to what tools to use based on the user's query. Note that we do not have `annotations` in our tool definition yet. We will see how to use them in the next section.

```json
[
  {
    "name": "calculate_bmi",
    "description": "Calculate BMI given weight in kg and height in centimeters.\n    \n    Args:\n        weight_kg: Weight in kilograms\n        height_cm: Height in centimeters\n        \n    Returns:\n        BMIResponse containing:\n            - bmi: Calculated BMI value\n            - category: BMI category (Underweight, Normal, Overweight, Obese)\n    ",
    "inputSchema": {
      "properties": {
        "weight_kg": {
          "description": "Weight in kilograms",
          "exclusiveMinimum": 0,
          "title": "Weight Kg",
          "type": "number"
        },
        "height_cm": {
          "description": "Height in centimeters",
          "exclusiveMinimum": 0,
          "title": "Height Cm",
          "type": "number"
        }
      },
      "required": [
        "weight_kg",
        "height_cm"
      ],
      "title": "calculate_bmiArguments",
      "type": "object"
    }
  }
]
```

Another example with 2 tools:

```json
[
  {
    "name": "hello_world",
    "description": "Returns a friendly greeting message",
    "inputSchema": {
      "properties": {
        "name": {
          "default": "World",
          "title": "Name",
          "type": "string"
        }
      },
      "title": "hello_worldArguments",
      "type": "object"
    }
  },
  {
    "name": "calculate_sum",
    "description": "Returns the sum of two numbers",
    "inputSchema": {
      "properties": {
        "a": {
          "title": "A",
          "type": "integer"
        },
        "b": {
          "title": "B",
          "type": "integer"
        }
      },
      "required": [
        "a",
        "b"
      ],
      "title": "calculate_sumArguments",
      "type": "object"
    }
  }
]
```



Note:
Since the LLM reads the tool’s description and matches it to the user’s request, it is important to provide a good description of the tool. This will help the LLM to understand what the tool does and how to use it. As such here are some guidelines:

**1. Clear Names and Descriptions:**
- Use names like get_weather or send_email, not vague ones like do_stuff.
- Write descriptions that explain exactly what the tool does.

**2. Validate Inputs:**
- Check that inputs match the schema (e.g., numbers for calculate_sum, not text).
- Prevent dangerous inputs (e.g., block invalid file paths in delete_file).

**3. Keep Tools Focused:**
- Each tool should do one thing well. Don’t make a tool that “does everything.”
- Example: Separate send_email and send_text_message instead of combining them.

**4. Handle Errors Gracefully:**
- If something goes wrong, return a clear error message instead of crashing.
- Example: If the weather API is down, return “Error: Could not fetch weather data.”

**5. Add Security:**
- Require authentication for sensitive tools (e.g., delete_file).
- Limit how often a tool can be used to prevent abuse.
- For a tool like execute_command, block dangerous commands like rm -rf / (which deletes everything)
- Log who uses tools and when, so you can spot suspicious activity.
- If a tool fails, don’t send detailed system errors to the client (e.g., database passwords).

**6. Use Annotations:**
- Mark destructive tools clearly so users know to be careful.
- Example: A tool that deletes files should have destructiveHint: true.


### More about Tool Annotations
Tool annotations are optional metadata added to a tool’s definition in MCP. They describe the tool’s behavior or purpose in a way that’s useful for:

- The LLM: To decide how to use the tool or warn about risks.
- The UI: To display the tool clearly to users or prompt for approval.
- Developers: To clarify the tool’s impact on the system or external world.

1. title
- Type: String
- Default: None (optional)
- What It Means: A short, human-friendly name for the tool, used in user interfaces (like an app or webpage) to make the tool easy to understand.
- When to Use:
  - When you want the tool to have a clear, descriptive name in the UI, especially for non-technical users.
  - Example: Instead of showing the tool’s technical name (get_weather), display “Check Weather” in a dropdown menu.
- Where It’s Useful:
  - In apps where users can manually select tools.
  - In approval prompts, so users know what the AI is trying to do.

Here's an example of a tool with the `title` annotation:

```python
# Define the get_weather tool
@mcp.tool(
    annotations={
        "title": "Check Weather",
    }
)
def get_weather(city: str = Field(..., description="City name")) -> WeatherResponse:
    """Fetch weather data for a given city (mock implementation).
    """
    # Mock weather data (in practice, this would call an API like OpenWeatherMap)
    mock_data = {
        "New York": {"temperature": 15.0, "condition": "Cloudy"},
        "London": {"temperature": 12.0, "condition": "Rainy"},
        "Tokyo": {"temperature": 20.0, "condition": "Sunny"}
    }
    if city in mock_data:
        return WeatherResponse(
            city=city,
            temperature=mock_data[city]["temperature"],
            condition=mock_data[city]["condition"]
        )
    raise ValueError(f"No weather data for city: {city}")
```

This is how the structure of the tool will look like:


```json
{
  "name": "get_weather",
  "description": "Fetches current weather for a city",
  "inputSchema": {
    "type": "object",
    "properties": {
      "city": { "type": "string" }
    },
    "required": ["city"]
  },
  "annotations": {
    "title": "Check Weather"
  }
}
```

2. readOnlyHint
- Type: Boolean
- Default: false
- What It Means: If true, the tool is “read-only,” meaning it doesn’t change anything in the system or external world (e.g., it only retrieves or computes data). If false, the tool might modify something.
- When to Use:
  - Use true for tools that only fetch or calculate data, like checking the weather or adding numbers.
  - Use false for tools that change something, like deleting a file or sending an email.
- Where It’s Useful:
  - Helps the AI decide if a tool is safe to run without human approval.
  - Informs the UI whether to show a warning or require confirmation.

Here's an example of a tool with the `readOnlyHint` annotation:

```python
@mcp.tool(
    annotations={
        "title": "Calculate Sum",  # Human-friendly name for UI display
        "readOnlyHint": True      # Tool only computes, doesn't modify anything
    }
)
def calculate_sum(
    a: float = Field(..., description="First number"),
    b: float = Field(..., description="Second number")
) -> float:
    """Adds two numbers.
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        The sum of a and b
    """
    return a + b
```

This is how the structure of the tool will look like:

```json
{
  "name": "calculate_sum",
  "description": "Adds two numbers",
  "inputSchema": {
    "type": "object",
    "properties": {
      "a": { "type": "number" },
      "b": { "type": "number" }
    },
    "required": ["a", "b"]
  },
  "annotations": {
    "title": "Calculate Sum",
    "readOnlyHint": true
  }
}
```

Note: A tool like delete_file would have `readOnlyHint: false` because it modifies the filesystem.

Set `readOnlyHint: true` only if the tool has no side effects (e.g., no writing to files, databases, or external APIs).

3. destructiveHint
- Type: Boolean
- Default: true
- What It Means: If true, the tool might cause irreversible changes (e.g., deleting data or overwriting files). This is only relevant when readOnlyHint is false.
- When to Use:
  - Use true for tools that can delete, overwrite, or permanently alter data or resources.
  - Use false for tools that make non-destructive changes, like adding a new record to a database.
- Where It’s Useful:
  - Alerts the AI and UI to warn users about risky actions.
  - Triggers confirmation prompts for dangerous operations.

Here's an example of a tool with the `destructiveHint` annotation:

```python
@mcp.tool(
    annotations={
        "title": "Delete File",      # Human-friendly name for UI display
        "readOnlyHint": False,      # Tool modifies the filesystem
        "destructiveHint": True     # Tool can cause irreversible data loss
    }
)
def delete_file(
    path: str = Field(..., description="Path to the file to delete")
) -> str:
    """Deletes a file from the server.
    
    Args:
        path: Path to the file to delete
        
    Returns:
        Confirmation message if deletion is successful
    """
    # Simulate file deletion (in practice, use os.remove(path))
    return f"File at {path} deleted successfully"
```

This is how the structure of the tool will look like:

```json
{
  "name": "delete_file",
  "description": "Deletes a file from the server",
  "inputSchema": {
    "type": "object",
    "properties": {
      "path": { "type": "string" }
    },
    "required": ["path"]
  },
  "annotations": {
    "title": "Delete File",
    "readOnlyHint": false,
    "destructiveHint": true
  }
}
```

4. idempotentHint
- Type: Boolean
- Default: false
- What It Means: If true, calling the tool multiple times with the same inputs has no additional effect (e.g., it’s safe to retry). This is only relevant when readOnlyHint is false.
- When to Use:
  - Use true for tools where repeating the same action doesn’t change the outcome, like setting a configuration to a specific value.
  - Use false for tools where each call could have a new effect, like sending an email or adding a record.
- Where It’s Useful:
  - Helps the AI decide if it’s safe to retry a failed tool call.
  - Informs the UI whether to allow repeated attempts without warning.

Here's an example of a tool with the `idempotentHint` annotation:

```python
@mcp.tool(
    annotations={
        "title": "Set User Role",    # Human-friendly name for UI display
        "readOnlyHint": False,      # Tool modifies user data
        "destructiveHint": False,   # Changes are not irreversible
        "idempotentHint": True      # Repeated calls with same inputs have no additional effect
    }
)
def set_user_role(
    userId: str = Field(..., description="ID of the user"),
    role: str = Field(..., description="Role to assign (e.g., admin, user)")
) -> str:
    """Sets a user’s role in the system.
    
    Args:
        userId: ID of the user
        role: Role to assign (e.g., admin, user)
        
    Returns:
        Confirmation message if role is set successfully
    """
    # Simulate setting the user's role (in practice, update a database)
    return f"User {userId} role set to {role}"
```

This is how the structure of the tool will look like:

```json
{
  "name": "set_user_role",
  "description": "Sets a user’s role in the system",
  "inputSchema": {
    "type": "object",
    "properties": {
      "userId": { "type": "string" },
      "role": { "type": "string" }
    },
    "required": ["userId", "role"]
  },
  "annotations": {
    "title": "Set User Role",
    "readOnlyHint": false,
    "destructiveHint": false,
    "idempotentHint": true
  }
}
```
If the LLM calls `set_user_role` with `userId: "123", role: "admin"`, calling it again with the same inputs won’t change anything (the user is already an admin). The LLM can safely retry if the first call fails.

Note: A tool like delete_file would have `idempotentHint: false` because each call could have a new effect.

Set `idempotentHint: true` only if the tool’s effect is the same no matter how many times it’s called with the same inputs.

5. openWorldHint
- Type: Boolean
- Default: true
- What It Means: If true, the tool interacts with external systems or the “open world” (e.g., the internet, APIs, or third-party services). If false, the tool works within a closed system (e.g., a local database or server).
- When to Use:
  - Use true for tools that call external APIs, access the web, or rely on unpredictable external systems.
  - Use false for tools that operate entirely within your controlled environment.
- Where It’s Useful:
  - Helps the AI anticipate potential delays or failures due to external dependencies.
  - Informs the UI to show a “connecting to external service” message or handle timeouts.

Here's an example of a tool with the `openWorldHint` annotation:

```python
@mcp.tool(
    annotations={
        "title": "Check Weather",    # Human-friendly name for UI display
        "readOnlyHint": True,       # Tool only fetches data, doesn't modify anything
        "openWorldHint": True       # Tool interacts with external systems (e.g., weather API)
    }
)
def get_weather(
    city: str = Field(..., description="Name of the city")
) -> str:
    """Fetches current weather for a city.
    
    Args:
        city: Name of the city (e.g., New York)
        
    Returns:
        Weather information as a string
    """
    # Simulate fetching weather data (in practice, call a weather API)
    return f"Weather in {city}: 20°C, Sunny"
```

This is how the structure of the tool will look like:

```json
{
  "name": "get_weather",
  "description": "Fetches current weather",
  "inputSchema": {
    "type": "object",
    "properties": {
      "city": { "type": "string" }
    },
    "required": ["city"]
  },
  "annotations": {
    "title": "Check Weather",
    "readOnlyHint": true,
    "openWorldHint": true
  }
}
```

The LLM knows that `get_weather` relies on an external weather API, so it might warn the user about possible delays. The UI could show a loading spinner while waiting for the API response.

Set `openWorldHint: true` if the tool depends on anything outside your server (e.g., APIs, web services).


Below is an example which uses all the annotations:

```python
@mcp.tool(
    annotations={
        "title": "Send Notification",  # Provides a human-friendly name for UI display, e.g., in a chatbot or app
        "readOnlyHint": False,        # Indicates the tool modifies state by sending a message
        "destructiveHint": False,     # Confirms the action is not irreversible or harmful
        "idempotentHint": False,      # Repeated calls send new messages, so not idempotent
        "openWorldHint": True         # Tool interacts with an external messaging service
    }
)
def send_notification(
    userId: str = Field(..., description="ID of the user to notify"),
    message: str = Field(..., description="Notification message content")
) -> str:
    """Sends a notification message to a user via an external service.
    
    Args:
        userId: ID of the user to receive the notification (e.g., email or Slack ID)
        message: Content of the notification message
        
    Returns:
        Confirmation message indicating the notification was sent
    """
    # Simulate sending a notification (in practice, this would call an external API like Slack or email service)
    return f"Notification sent to user {userId}: {message}"
```

This is how the structure of the tool will look like:

```json
{
  "name": "send_notification",
  "description": "Sends a notification message to a user via an external service",
  "inputSchema": {
    "type": "object",
    "properties": {
      "userId": { "type": "string" },
      "message": { "type": "string" }
    },
    "required": ["userId", "message"]
  },
  "annotations": {
    "title": "Send Notification",
    "readOnlyHint": false,
    "destructiveHint": false,
    "idempotentHint": false,
    "openWorldHint": true
  }
}
```


Now if we update our bmi calculator to use all the annotations, it will look like this:

```python
@mcp.tool(
    annotations={
        "title": "Calculate BMI",       # Provides a human-friendly name for UI display, e.g., in a health app
        "readOnlyHint": True,          # Indicates the tool only computes BMI and doesn't modify anything
        "destructiveHint": False,      # Confirms the action has no destructive effects (irrelevant since readOnlyHint is True)
        "idempotentHint": True,        # Repeated calls with same inputs produce the same BMI result
        "openWorldHint": False         # Tool performs local computation, no external systems involved
    }
)
def calculate_bmi(
    weight_kg: float = Field(..., description="Weight in kilograms", gt=0),
    height_cm: float = Field(..., description="Height in centimeters", gt=0)
) -> BMIResponse:
  ...
```


### Error Handling
The error handling guideline for MCP tools emphasizes that errors should be reported in a structured way within the tool’s result object, rather than as protocol-level errors (e.g., HTTP 500 errors). This ensures that the LLM can handle errors gracefully and provide appropriate feedback to the user.

Key points:

1. Set `isError` to `True` in the Result:
The result object (e.g., `types.CallToolResult`) includes an `isError` field. Setting it to `True` signals that the tool execution failed.
This allows the LLM to distinguish between successful results and errors.

2. Include Error Details in the `content` Array:
The `content` array contains `types.TextContent` objects with error details (e.g., a descriptive message like “Invalid input”).
This provides context about what went wrong, which the LLM can use to inform the user or take corrective action.


```python
@mcp.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> types.CallToolResult:
    """Handle requests to execute a tool, with proper error handling.
    
    Args:
        name: Name of the tool (e.g., "calculate_sum")
        arguments: Input parameters (e.g., {"a": 5, "b": 3})
        
    Returns:
        CallToolResult with content and isError flag, following MCP error handling guidelines
        
    Raises:
        ValueError: If the tool name is not found
    """
    if name == "calculate_sum":
        try:
            # Execute the calculate_sum tool with provided inputs
            result = calculate_sum(
                a=arguments["a"],
                b=arguments["b"]
            )
            # Return successful result in CallToolResult
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Operation successful: {result}"
                    )
                ]
            )
        except Exception as error:
            # Handle errors by returning CallToolResult with isError=True
            # This allows the LLM to see and potentially handle the error
            return types.CallToolResult(
                isError=True,
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Error: {str(error)}"
                    )
                ]
            )
    raise ValueError(f"Tool not found: {name}")

```

That is it for tools in MCP!

