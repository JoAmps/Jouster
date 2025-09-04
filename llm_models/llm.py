from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from data_validator.data_valid import BlogDetails

# Load environment variables
load_dotenv()


class LLMHandler:
    """
    Handles interaction with OpenAI's GPT models using LangChain's ChatOpenAI class.
    Provides methods to obtain configured LLMs for analyzing blog or article text:
    - Raw LLM for general-purpose usage
    - Structured LLM for extracting BlogDetails (title, topics, sentiment, keywords, summary)

    Uses environment variables for API configuration.
    """

    def __init__(self):
        """
        Initializes the LLMHandler with API credentials from environment variables.

        Attributes:
            api_key (str): OpenAI API key for authentication.
            model_name (str): Model name (e.g., 'gpt-4o-mini') to use with ChatOpenAI.
        """
        self.api_key = os.getenv("openai_api_key")
        self.model_name = os.getenv("model_name")

        # Validate environment configuration
        if not self.api_key or not self.model_name:
            raise ValueError(
                "❌ OpenAI API key and model name must be provided in environment variables."
            )

    def get_llm(self):
        """
        Creates and returns a general ChatOpenAI instance.

        Returns:
            ChatOpenAI: Instance configured with the API key and model name.

        Raises:
            RuntimeError: If the LLM instantiation fails.
        """
        try:
            return ChatOpenAI(model_name=self.model_name, openai_api_key=self.api_key)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to initialize LLM: {str(e)}") from e

    def blog_llm(self):
        """
        Returns a ChatOpenAI instance configured for structured blog analysis.

        The returned model outputs structured JSON matching the BlogDetails schema
        (title, topics, sentiment, keywords, summary).

        Returns:
            ChatOpenAI: An instance set up to produce structured BlogDetails output.

        Raises:
            RuntimeError: If the structured LLM instantiation fails.
        """
        try:
            return self.get_llm().with_structured_output(BlogDetails)
        except Exception as e:
            raise RuntimeError(
                f"❌ Failed to initialize BlogDetails LLM: {str(e)}"
            ) from e
