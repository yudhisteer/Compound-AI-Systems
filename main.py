import json

from pydantic import BaseModel

from autogen import ConversableAgent


# 1. Define our lesson plan structure, a lesson with a number of objectives
class LearningObjective(BaseModel):
    title: str
    description: str


class LessonPlan(BaseModel):
    title: str
    learning_objectives: list[LearningObjective]
    script: str


# 2. Add our lesson plan structure to the LLM configuration
llm_config = {
    "api_type": "openai",
    "model": "gpt-4o-mini",
    "response_format": LessonPlan,
}

# 3. The agent's system message doesn't need any formatting instructions
system_message = """You are a classroom lesson agent.
Given a topic, write a lesson plan for a fourth grade class.
"""

my_agent = ConversableAgent(
    name="lesson_agent",
    llm_config=llm_config,
    system_message=system_message
    )

# 4. Chat directly with our agent
chat_result = my_agent.run("In one sentence, what's the big deal about AI?")

# 5. Get and print our lesson plan
lesson_plan_json = json.loads(chat_result.chat_history[-1]["content"])
print(json.dumps(lesson_plan_json, indent=2))