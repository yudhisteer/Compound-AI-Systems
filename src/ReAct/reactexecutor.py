from typing import List
from common import Agent, AgentConfig, ReactEnd

import logging

from util import logger_setup

# Initialize logger
logger = logging.getLogger(__name__)


class ReactExecutor:
    def __init__(self, agent: List[Agent], config: AgentConfig) -> None:
        self.base_agent = agent
        self.config = config
        self.request = ""

    def __thought(self, current_agent: Agent) -> None:
        """
        Reason about the next action to take.
        """
        pass

    def __action(self, current_agent: Agent) -> Agent:
        """
        Decide on an action to take.
        """
        pass

    def __observation(self, current_agent: Agent) -> ReactEnd:
        """
        Execute action and feedback observation.
        """
        pass


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
            total_interactions += 1
            self.__thought(agent) # Thinks about what to do
            agent = self.__action(agent) # Takes an action
            observation = self.__observation(agent) # Observes the result
            if observation.stop: # True if the context is enough to answer the request
                logger.info(f"Final Answer: {observation.final_answer}")
                return observation.final_answer 
            
            if self.config.max_interactions <= total_interactions:
                logger.info("Max interactions reached. Exiting...")
                return "" # returns empty string if max interactions reached








