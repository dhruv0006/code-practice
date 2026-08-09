import json


class Summarizer:
    """
    Responsible for converting the text description into a meaningful summary
    using the LLM client.
    """

    def __init__(self, client, system_prompt):
        self.client = client
        self.system_prompt = system_prompt

    def summarize(self, description, max_words, style):
        # Build a plain instruction for the model
        user_content = (
            f"Summarize the following text in at most {max_words} words, "
            f"as a {style}.\n\nText:\n{description}"
        )

        # Build messages in the chat format
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_content},
        ]

        # Call the LLM client
        response = self.client.chat_completion(messages)

        # Extract text from LLM response
        llm_answer = self.client.extract_response_text(response)

        return llm_answer