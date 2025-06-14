
import uuid
import time

from src.command import Command, Prompt, prompt_to_json
from src.rag_service.dao import get_database
from src.config import Config
from src.rag_service.embeddings import create_embeddings_model
from src.LLM import LLM, create_llm


def getAnswerFromUser(answer: str, target: str, question: str, model = "gemini") -> str:
    """Get the answer from the user. Target is what the question is about. Example: "What is your name?" -> target= "name"."""
    prompt = ""
    if target == "name":
    
        prompt = """A user has provided the following answer to the question: {question}. 
                        The answer is: {answer}. The question is about the user's {target} You are to ONLY REPLY IN JSON FORMAT like so:
                        target: "some answer"
                        An example of a valid response is for the question "What is your name?" where target is name and answer from user is My name is John Doe is:
                        name: "John Doe"
                    """
    else :
        prompt = """A user has provided the following answer to the question: {question}. 
                        The answer is: {answer}. The question is about the user's {target} You are to ONLY REPLY IN JSON FORMAT like so:
                        target: "some answer"
                        When the target is user_mode, you shall review the answer and categorize it as either "experienced, beginner, or unsure".
                        An example of a valid response is for the question "What is your name?" where target is user_mode and answer from user is "I am not experienced with VR" is:
                        user_mode: "beginner"
                    """
    prompt.format(answer=answer, target=target, question=question)
    # skoleelev
    # unge arbeidsledige
    # studerer fagskole
    # om de har jobberfaring
    # Nettopp ferdig med skole?
    # arbeidsløs en stund
    # har de vært i jobb før?
    # har de hatt praksis tidligere i et relevant felt? 
    # interests?
    
    language_model = create_llm(model)
    response = language_model.generate(prompt)
    if response is None:
        return "No response from the language model."
    if response == "":
        return "Empty response from the language model."
    
    return response


def assemble_prompt(command: Command, model: str = "gemini") -> dict[str]:
    """Assembles a prompt for a large language model and prompt LLM to generate a response."""
    
    #to_embed: str = str(command.question) + " "+ str(command.progress) + " "+ str(command.user_actions)
    
    #to_embed: str = str(command.chatLog[-1].content)
    to_embed: str = str(command.chatLog[-1].content) if command.chatLog else "No user message"

    
    db = get_database()
    embedding_model = create_embeddings_model()
    embeddings: list[float] = embedding_model.get_embedding(to_embed)
    context = db.get_context("hello", embeddings ) # TODO: remove document name from here
    
    base_prompt = """
    MANDATORY: 
    If you detect the user needs an action, you MUST guess the appropriate function call using [FUNCTION]function_name|parameter[/FUNCTION].
    If you are unsure, make your best guess. DO NOT return an empty response.

    You are a helpful assistant and guide in the Blue Sector Virtual Reality work training. 
    You are here to help the user with their questions and guide them through the training.

    Earlier chathistory is: {command.chatLog}
    The user is currently in the {command.scene_name} scene. When the user asks a question from {command.scene_name} = ReceptionOutdoor, your name is Rachel. When the user asks a question from {command.scene_name} = Laboratory, your name is Larry.

    The information you have obtained on the user is {command.user_information}. ADJUST YOUR ANSWER BASED ON THIS, IF IT IS AVAILABLE. IF TWO ANSWERS TO THE SAME QUESTION ARE GIVEN, USE THE LATEST ONE.
    IF TWO ANSWERS CONTRADICT EACH OTHER, USE THE LATEST ONE.
    If user information is unavailable, try to provide a general answer.
    The user has made the following progress: {command.progress}.
    The user has taken the following actions: {command.user_actions}. (Actions may not be available) Refer to these when a user asks about an object they have interacted with.
    IF THERE ARE NO CONTEXT AVAILABLE, PLEASE STATE THAT YOU ARE NOT SURE, BUT TRY TO PROVIDE AN ANSWER.
    PROVIDE A SHORT ANSWER THAT IS EASY TO UNDERSTAND. STATE THE NAME OF THE USER IN A NATURAL WAY IN THE RESPONSE.

    IMPORTANT - FUNCTION CALLING INSTRUCTIONS:
    When the user asks to move to a different location or scene, or when you need to assist them by showing objects or playing animations,
    follow this two-step confirmation process:

    1. First, ask the user to confirm the action you're about to perform. For example:
       "Would you like me to teleport you to the Laboratory?" or "Shall I show you the safety equipment?"
    
    2. Only after the user confirms, use the function calling format as your next response:
       [FUNCTION]function_name|parameter[/FUNCTION]
    
    If the user has already explicitly confirmed in their current message, you may execute the function immediately.

    IMPORTANT CONSTRAINTS:
    - NEVER teleport the user to the scene they are currently in. If they ask to go to their current location, inform them they are already there.

    Function call format:
    [FUNCTION]function_name|parameter[/FUNCTION]

    Available functions:
    - teleport(location: str): Teleport the user to a specific scene. Available scenes are:
        * ReceptionOutdoor - The main reception area
        * Laboratory - Where scientific experiments take place
    If the user asks to go to any of these locations or expresses a desire to move to another area, follow the confirmation process.
    REMEMBER: Do not teleport the user to their current scene location.

    - showObject(objectId: str): Highlight or show a specific object to the user.

    Example 1: If the user says "Can you take me to the lab?", respond with:
    "Would you like me to teleport you to the Laboratory? Please confirm."
    
    Example 2: If the user then confirms "Yes, please", respond with:
    "[FUNCTION]teleport|Laboratory[/FUNCTION]"
    
    Example 3: If the user says "Yes, teleport me to the reception right now", you can respond directly with:
    "[FUNCTION]teleport|ReceptionOutdoor[/FUNCTION]"

    Example 4: If the user says "Take me to the Laboratory" but they are already in the Laboratory scene, respond with:
    "You're already in the Laboratory. Is there something specific you're looking for here?"
    
    Answer in a SHORT and UNDERSTANDABLE way, NOT exceeding 200 characters.
    """
    
    base_prompt = base_prompt.format(command=command)
    prompt: str = ""
    if context is None or len(context) == 0:
        prompt += str(base_prompt) + "context: NO CONTEXT AVAILABLE " + "question: " +  str(command.chatLog[-1])
    
    else:
        prompt += str(base_prompt) + "context: " + str(context[0])+ "question: "+ str(command.chatLog[-1])

    print(f"Prompt sent to LLM:\n{prompt}")

    language_model = create_llm(model)
    response = language_model.generate(prompt)
    
    # Parse the response for function calls
    function_call = None
    parsed_response = response

    import re
    function_match = re.search(r'\[FUNCTION\](.*?)\|(.*?)\[\/FUNCTION\](.*)', response, re.DOTALL)
    if function_match:
        function_name = function_match.group(1).strip()
        function_param = function_match.group(2).strip()
        
        function_tag_text = function_match.group(0)
        parsed_response = response.replace(function_tag_text, "").strip()

        function_call = {
            "function_name": function_name,
            "function_parameters": [function_param]
        }
    
    return {
        "id": str(uuid.uuid4()),
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": parsed_response,
                    "function_call": function_call
                },
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            # "prompt_tokens": prompt_token_count,
            # "completion_tokens": completion_token_count,
            # "total_tokens": total_tokens
        },
        "system_fingerprint": "v1-system",  # placeholder
        "context_used": context if context else [],
        "metadata": {
            "response_length": len(parsed_response),
            # "confidence_score": 0.95
        },
        "response": parsed_response,
        "function_call": function_call
    }



