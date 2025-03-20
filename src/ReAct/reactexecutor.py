import inspect
import json
import logging
from typing import List

from util import logger_setup
from .brain import Brain
from .common import Agent, AgentConfig, ReactEnd, Tool, ToolChoice

# Initialize logger
logger = logging.getLogger(__name__)


class ReactExecutor:
    def __init__(self, agent: List[Agent], config: AgentConfig) -> None:
        self.base_agent: Agent = agent
        self.config: AgentConfig = config
        self.request: str = ""
        self.brain: Brain = Brain(config)

    @staticmethod
    def __get_tools(agent: Agent) -> str:
        """
        Helper function to get the tools from the agent.
        Example output:
            ```
            people_search - Use this tool to search for information about people.                                                                                
            calculator - Use this tool to perform calculations.
            date - Use this tool to get the current date.
            ```
        Will be used to create the prompt for the LLM to choose the tool.
        """
        # check if the tool is a tool and not an Agent
        tools = [tool for tool in agent.functions if isinstance(tool, Tool)]
        # Create a list that combines the name and description of each tool                                        
        str_tools = [tool.name + " - " + tool.desc for tool in tools]
        # Join the strings in the list with a newline character.
        return "\n".join(str_tools)

    def __thought(self, current_agent: Agent) -> None:
        """
        Reason about the next action to take.
        """
        tools = self.__get_tools(current_agent)
        prompt = f"""Answer the following request as best you can: {self.request}.
            
        First think step by step about what to do. Plan step by step what to do.
        Continuously adjust your reasoning based on intermediate results and reflections, adapting your strategy as you progress.
        Your goal is to demonstrate a thorough, adaptive, and self-reflective problem-solving process, emphasizing dynamic thinking and learning from your own reasoning.

        Make sure to include the available tools in your plan.

        Your available tools are: 
        {tools} 

        CONTEXT HISTORY:
        ---
        {self.brain.recall()}
        """

        response = self.brain.think(prompt=prompt, agent=current_agent)
        print(f"===================Thought===================")
        print(f"Thought: {response} \n")
        # Store AI assistant's response in conversation history
        self.brain.remember("Assistant: " + response)

    def __action(self, agent: Agent) -> tuple[Agent, bool]:
        """
        Decide on an action to take.
        """
        tool = self.__choose_tool(agent)
        # if the tool exist
        if tool:
            # SCENARIO 1: When the tool is another agent
            # we check if the tool is an Agent
            if isinstance(tool.func, Agent):
                # assign the tool as an agent (tool.func is already an agent)
                agent = tool.func
                logger.info(f"New agent: {agent.name} \n")
                return agent, True

            # SCENARIO 2: When no tool is available and control returns to the base agent
            # Execute the tool
            self.__execute_tool(tool, agent)

        else:
            logger.info("No tool to execute")
            # when we do not have a tool, we use use current base agent
            agent = self.base_agent
            return agent, True

        return agent, False

    def __observation(self, current_agent: Agent) -> ReactEnd:
        """
        Execute action and feedback observation.
        """
        return ReactEnd(
            stop=True, final_answer="This is the final answer", confidence=0.7
        )



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

    def __execute_tool(self, tool: Tool, agent: Agent):
        """
        Execute the tool.
        """
        if tool is None:
            logger.info("Tool is None")
            return None

        # find parameters for tool
        parameters = inspect.signature(tool.func).parameters

        # TODO: Ask LLM to fill parameters
        # "parameter_name": <function parameter>, E.g. "operation": <function parameter>, "a": <function parameter>, "b": <function parameter>
        response = f"""
        {{
            {', '.join([f'"{param}": <function parameter>' for param in parameters])}
        }}"""
        logger.info(f"Response: {response}")

        try:
            resp = json.loads(response)
        except json.JSONDecodeError:
            logger.error("Invalid JSON response from LLM")
            return

        tool_result = tool.func(**resp)
        logger.info(f"Tool result: {tool_result}")



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
            # When we switch to a new agent, we want that agent to start its own thought-action-observation cycle
            if skip:
                continue  # skip the current iteration
            observation = self.__observation(agent)  # Observes the result
            if observation.stop:  # True if the context is enough to answer the request
                logger.info(f"Final Answer: {observation.final_answer}")
                return observation.final_answer
