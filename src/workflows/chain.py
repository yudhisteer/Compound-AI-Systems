from src.utils.utils import get_chat_completion, chain_workflow

# Based on: https://github.com/anthropics/anthropic-cookbook/blob/main/patterns/agents/basic_workflows.ipynb


if __name__ == "__main__":

    data_processing_steps = [
    """Extract all store units and their sales numbers.
    Format as 'store: units'.
    Example:
    NY: 123 units
    LA: 46 units""",

    """Standardize all numbers to thousands (K).
    Format as 'store: number K'.
    Example:
    NY: 0.12K
    LA: 0.046K""",

    """Rearrange the data in ascending order of units sold.
    Format as 'store: units'.
    Example:
    NY: 10K units
    LA: 46K units""",

    """Generate sales analysis table:
    | Store | Units (K) |
    | NY    | 0.16K     |
    | LA    | 0.046K    |"""
    ]      

    report = """Q1 Sales Report:
    NY store sold 15600 units
    LA store sold 23400 units
    Miami store sold 8900 units
    Chicago store sold 17800 units
    Houston store sold 20300 units"""

    print("Starting chain workflow...\n\nReport:\n", report)

    result = chain_workflow(report, data_processing_steps, debug=True)
    print("\n\nResult:\n", result)
