"""Module for storing and retrieving agent instructions.

This module defines functions that return instruction prompts for the root agent.
These instructions guide the agent's behavior, workflow, and tool usage.
"""


def return_instructions_root() -> str:

    instruction_prompt_root = """
        You are an AI assistant designed to help users with what they need.
    """

    return instruction_prompt_root