import os
import sys

from openai import OpenAI
from pydantic import BaseModel
from util.utils import get_chat_completion_parse


class Person(BaseModel):
    name: str
    age: int
    email: str


if __name__ == "__main__":

    system_prompt = "You are a helpful assistant that extracts information about a person from a text."
    user_prompt = "Olive is 25 years old and his email is sam@example.com."

    person = get_chat_completion_parse(system_prompt, user_prompt, Person)

    print("Name:", person.name)
    print("Age:", person.age)
    print("Email:", person.email)
