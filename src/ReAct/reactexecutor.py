from typing import List
from common import Agent, AgentConfig

class ReactExecutor:
    def __init__(self, agent: List[Agent], config: AgentConfig) -> None:
        self.base_agent = agent
        self.config = config
        self.request = ""

    def __thought(self, current_agent: Agent) -> None:
        """
        This function is used to generate the thought of the current agent.
        """
        pass

    def __action(self, current_agent: Agent) -> None:
        """
        This function is used to take action based on the thought by the current agent.
        """
        pass

    def __observation(self, current_agent: Agent) -> None:
        """
        This function is used to observe the outcome of the action taken by the current agent.
        """
        pass


    def execute(self, request: str) -> None:
        """
        This function is used to execute the request.
        """
        self.request = request
        current_agent = self.base_agent
        self.__thought(current_agent)
        self.__action(current_agent)
        return self.__observation(current_agent)




