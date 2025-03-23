import json
from enum import Enum


def filter_content(contexts: list, option: str):
    """Filter contexts based on the option selected by the llm."""
    for i, context in enumerate(contexts):
        if f"{i}" == option.lower():
            return [context]
        if f"option {i}" == option.lower():
            return [context]
    return contexts


class EnumEncoder(json.JSONEncoder):
    """JSON encoder for Enum objects."""

    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value

        return super().default(obj)


if __name__ == "__main__":

    contexts = [
        "This is the first document with some information.",
        "This is the second document with different information.",
        "This is the third document with additional details.",
    ]

    # Example 1: Select context by index number
    selected_option = "1"  # This will select the second context (index 1)
    filtered_results = filter_content(contexts, selected_option)
    print(
        filtered_results
    )  # Output: ["This is the second document with different information."]

    # Example 2: Select context by "option {index}" format
    selected_option = "option 2"  # This will select the third context (index 2)
    filtered_results = filter_content(contexts, selected_option)
    print(
        filtered_results
    )  # Output: ["This is the third document with additional details."]

    # Example 3: If option doesn't match any pattern, all contexts are returned
    selected_option = "something else"
    filtered_results = filter_content(contexts, selected_option)
    print(filtered_results)  # Output: [all three original contexts]

    class DocumentType(Enum):
        TEXT = "text"
        PDF = "pdf"
        WEBPAGE = "webpage"

    document = {
        "id": 123,
        "content": "This is sample content",
        "type": DocumentType.PDF,
    }

    # Without EnumEncoder, this would raise a TypeError
    # With EnumEncoder, it properly converts the Enum to its value
    json_string = json.dumps(document, cls=EnumEncoder, indent=2)
    print(json_string)
    # Output:
    # {
    #   "id": 123,
    #   "content": "This is sample content",
    #   "type": "pdf"
    # }
