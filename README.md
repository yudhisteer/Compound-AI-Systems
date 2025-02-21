# Autonomous-Multi-Agent-Framework-using-AutoGen

## Plan of Action
1. [Understanding Agents](#understanding-agents)
2. [Workflow: Prompt chaining](#workflow-prompt-chaining)
3. [Workflow: Routing](#workflow-routing)
4. [Workflow: Parallelization](#workflow-parallelization)
5. [Workflow: Orchestrator-workers](#workflow-orchestrator-workers)
6. [Workflow: Evaluator-optimizer](#workflow-evaluator-optimizer)

--------

<a name="understanding-agents"></a>
## 1. Understanding Agents





```python
def chain_workflow(query: str, steps: list[str]) -> str:
    """
    Execute a chain of workflows.
    """
    input_query = query
    for i, step in enumerate(steps):
        input_prompt = f"Step {i+1}:\n{step}\n\nQuery:\n{input_query}"
        input_query = get_chat_completion(input_prompt)
    return input_query
```

```python
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
```


```python
Step 1:
Extract all store units and their sales numbers.
    Format as 'store: units'.
    Example:
    NY: 123 units
    LA: 46 units

Result:
Here are the extracted store units and their sales numbers:

NY: 15600 units
LA: 23400 units
Miami: 8900 units
Chicago: 17800 units
Houston: 20300 units

--------------------------------------------------------------------------------
Step 2:
Standardize all numbers to thousands (K).
    Format as 'store: number K'.
    Example:
    NY: 0.12K
    LA: 0.046K

Result:
Here are the standardized sales numbers formatted as requested:

NY: 15.6K
LA: 23.4K
Miami: 8.9K
Chicago: 17.8K
Houston: 20.3K

--------------------------------------------------------------------------------
Step 3:
Rearrange the data in ascending order of units sold.
    Format as 'store: units'.
    Example:
    NY: 10K units
    LA: 46K units

Result:
Here is the data rearranged in ascending order of units sold:

Miami: 8.9K
NY: 15.6K
Chicago: 17.8K
Houston: 20.3K
LA: 23.4K

--------------------------------------------------------------------------------
Step 4:
Generate sales analysis table:
    | Store | Units (K) |
    | NY    | 0.16K     |
    | LA    | 0.046K    |

Result:
Based on the provided data, here is the sales analysis table rearranged in ascending order of units sold:

| Store  | Units (K) |
|--------|-----------|
| LA     | 0.046K    |
| NY     | 0.16K     |
| Miami  | 8.9K      |
| Chicago| 17.8K     |
| Houston| 20.3K     |

```

-------------

<a name="workflow-prompt-chaining"></a>
## 2. Workflow: Prompt chaining

-------------




## References
1. https://docs.ag2.ai/docs/Home
2. https://github.com/anthropics/anthropic-cookbook/tree/main/patterns/agents
3. https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/
4. https://www.anthropic.com/research/building-effective-agents
5. https://github.com/AGI-Edgerunners/LLM-Agents-Papers
5. https://github.com/zjunlp/LLMAgentPapers
6. https://research.google/blog/chain-of-agents-large-language-models-collaborating-on-long-context-tasks/
7. https://www.ycombinator.com/library/Lt-vertical-ai-agents-could-be-10x-bigger-than-saas
