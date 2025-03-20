


```python
def __choose_tool(self, agent: Agent) -> Tool:
    """
    Choose the tool to use.
    """
    # TODO: Ask LLM to choose the tool
    # Hardcodedto select people_search
    response: ToolChoice = ToolChoice(
        tool_name="people_search",
        reason_of_choice="We need to search for information about people.",
    )
    tool = [tool for tool in agent.functions if tool.name == response.tool_name]
    logger.info(f"Tool: {tool}") # output Tool: [<src.ReAct.common.Tool object>] in first log
    return tool[0] if tool else None
```

```python
def __action(self, agent: Agent) -> tuple[Agent, bool]:
    """
    Decide on an action to take.
    """
    tool = self.__choose_tool(agent)
    # if the tool exist
    if tool:
        # we check if the tool is an Agent
        if isinstance(tool.func, Agent):
            # assign the tool as an agent (tool.func is already an agent)
            agent = tool.func
            logger.info(f"New agent: {agent.name}")
            return agent, True

        # Execute the tool
        self.__execute_tool(tool, agent)

    else:
        logger.info("No tool to execute")
        # when we do not have a tool, we use use current base agent
        agent = self.base_agent
        return agent, True

    return agent, False
```

```python
    def execute(self, query_input: str) -> str:
        """
        Loop Workflow
        -------------
        Input Query → [THINK → ACT → OBSERVE] → Final Answer
                        ↑__________________|
                        (repeats until done)
        """
        logger.info(f"Request: {query_input}")
        self.request = query_input
        total_interactions = 0
        agent = self.base_agent
        while True:
            print(f"\nIteration no: {total_interactions+1}")
            total_interactions += 1
            if self.config.max_interactions <= total_interactions:
                logger.info("Max interactions reached. Exiting...")
                return ""  # returns empty string if max interactions reached

            self.__thought(agent)  # Thinks about what to do

            # we will be retrieving the tool and the tool can be another agent
            # if the agent is different from the base agent, we will skip.
            agent, skip = self.__action(agent)  # Takes an action
            if skip:
                continue  # skip the current iteration
            observation = self.__observation(agent)  # Observes the result
            if observation.stop:  # True if the context is enough to answer the request
                logger.info(f"Final Answer: {observation.final_answer}")
                return observation.final_answer
            
```

```python
2025-03-19 09:48:39,491 | src.ReAct.reactexecutor | INFO | reactexecutor.py:109 | Request: What is the half of Einstien's age?

Iteration no: 1
2025-03-19 09:48:39,492 | src.ReAct.reactexecutor | INFO | reactexecutor.py:70 | Tool: [<src.ReAct.common.Tool object at 0x000001EEA31F3740>]
2025-03-19 09:48:39,493 | src.ReAct.reactexecutor | INFO | reactexecutor.py:37 | New agent: people_search_agent

Iteration no: 2
2025-03-19 09:48:39,494 | src.ReAct.reactexecutor | INFO | reactexecutor.py:70 | Tool: []
2025-03-19 09:48:39,494 | src.ReAct.reactexecutor | INFO | reactexecutor.py:44 | No tool to execute

Iteration no: 3
2025-03-19 09:48:39,495 | src.ReAct.reactexecutor | INFO | reactexecutor.py:70 | Tool: [<src.ReAct.common.Tool object at 0x000001EEA31F3740>]
2025-03-19 09:48:39,495 | src.ReAct.reactexecutor | INFO | reactexecutor.py:37 | New agent: people_search_agent

Iteration no: 4
2025-03-19 09:48:39,496 | src.ReAct.reactexecutor | INFO | reactexecutor.py:70 | Tool: []
2025-03-19 09:48:39,496 | src.ReAct.reactexecutor | INFO | reactexecutor.py:44 | No tool to execute

Iteration no: 5
2025-03-19 09:48:39,497 | src.ReAct.reactexecutor | INFO | reactexecutor.py:117 | Max interactions reached. Exiting...
```

1. **First Iteration**:
   - Starts with base agent
   - `__choose_tool` finds "people_search" tool
   - `__action` sees it's an Agent and switches to `people_search_agent`
   - Logs: `Tool: [<Tool object>]` and `New agent: people_search_agent`

2. **Second Iteration**:
   - Now using `people_search_agent`
   - `__choose_tool` looks for "people_search" in this agent's functions
   - No tool found (empty list)
   - `__action` reverts to base agent
   - Logs: `Tool: []` and `No tool to execute`

3. **Third Iteration**:
   - Back to base agent
   - Same as first iteration
   - Logs: `Tool: [<Tool object>]` and `New agent: people_search_agent`

4. **Fourth Iteration**:
   - Same as second iteration
   - Logs: `Tool: []` and `No tool to execute`

5. **Fifth Iteration**:
   - System hits maximum iteration limit (5)
   - Logs: `Max interactions reached. Exiting...`