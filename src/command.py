from pydantic import BaseModel
from pydantic import ValidationError
from typing import Optional
from src.models.progress import ProgressData
from src.models.message import Message
import json


class Command(BaseModel):
    """Message from the VR application about the current state. This is an loose implementation of the command pattern
    """
    user_information: Optional[dict] = None
    progress: list[ProgressData]
    user_actions: list[str]
    NPC: int
    chatLog: list[Message]


class Prompt(BaseModel):
    """Message to be passed to a large language model."""
    user_information: Optional[dict] = None
    question: str
    progress: list[ProgressData]
    user_actions: list[str]
    base_prompt: str
    context: str


def prompt_to_json(prompt: Prompt) -> str:
    """Converts a Prompt instance to a JSON string."""
    return prompt.model_dump_json()



def command_from_json(json_str: str) -> Optional[Command]:
    """Parses a JSON string into a Command object.
    
    Args:
        json_str (str): The JSON string representing a Command.

    Returns:
        Optional[Command]: The Command object if parsing is successful, otherwise None.
    """
    try:
        return Command.model_validate_json(json_str)
    except ValidationError as e:
        print("Validation error:", e)
        return None
