from data_validator.data_valid import BlogBuilderState
from langgraph.types import interrupt
from llm_models.llm import LLMHandler
import nltk
from collections import Counter
from nltk.corpus import stopwords


class BlogDetails:
    """
    Handles blog/article detail extraction using LLMs and basic NLP.

    Responsibilities:
    - Ask the user for input text (blog/article).
    - Use LLM to extract title, topics, and sentiment.
    - Use LLM to generate a short summary.
    - Use NLTK to extract top frequent keywords (nouns).
    """

    def ask_blog_details(self, state: BlogBuilderState) -> BlogBuilderState:
        """
        Interrupt the workflow to request blog/article input from the user.

        Args:
            state (BlogBuilderState): Current state of the workflow.

        Returns:
            BlogBuilderState: Updated state with 'user_input' field set after user response.
        """
        user_input = interrupt(
            "Kindly drop the article or blog post you want to generate details for."
        )
        state["user_input"] = user_input
        return state

    def collect_blog_details(self, state: BlogBuilderState) -> BlogBuilderState:
        """
        Extract title, topics, and sentiment from the user-provided input using an LLM.

        Args:
            state (BlogBuilderState): Current state containing 'user_input'.

        Returns:
            BlogBuilderState: Updated state with 'title', 'topics', and 'sentiment' if valid.
            If invalid or LLM fails, interrupts with a retry request.
        """
        user_input = state.get("user_input")

        if not user_input:
            return interrupt(
                "You didn’t provide any input. Please drop the article or blog post you want to analyze."
            )

        prompt = f"""
        Extract the following from the input:
        1. title: str
        2. topics: List[str]
        3. sentiment: Literal["positive", "neutral", "negative"]

        If you CANNOT confidently extract the topics and sentiment return:
        {{
            "topics": "INVALID",
            "sentiment": "INVALID"
        }}

        Input: "{user_input}"
        """

        try:
            response = LLMHandler().blog_llm().invoke(prompt)
            title = response.title
            topics = response.topics
            sentiment = response.sentiment
        except Exception as e:
            # Graceful LLM failure
            return interrupt(f"LLM error while extracting blog details: {str(e)}")

        if topics != "INVALID" and sentiment != "INVALID":
            state["title"] = title
            state["topics"] = topics
            state["sentiment"] = sentiment
            return state
        else:
            return interrupt(
                "Sorry, try again. Kindly drop the article or blog post you want to generate details for."
            )

    def generate_summary(self, state: BlogBuilderState) -> BlogBuilderState:
        """
        Generate a 1–2 sentence summary of the user-provided input using an LLM.

        Args:
            state (BlogBuilderState): Current state containing 'user_input'.

        Returns:
            BlogBuilderState: Updated state with 'summary'.
            If LLM fails, stores the error message instead.
        """
        user_input = state.get("user_input")

        prompt = f"""
            You are an AI assistant. Summarize the following article or blog in **1-2 concise sentences**, 
            capturing the main idea and key points. Avoid adding personal opinions or extra details.

            Article/Blog Text:
            {user_input}

            Summary:
            """

        try:
            response = LLMHandler().get_llm().invoke(prompt)
            state["summary"] = response.content
        except Exception as e:
            state["summary"] = f"LLM error: {str(e)}"

        return state

    def get_keywords(self, state: BlogBuilderState, top_n: int = 3) -> BlogBuilderState:
        """
        Extract the top-N most frequent nouns (keywords) from user input.

        Args:
            state (BlogBuilderState): Current state containing 'user_input'.
            top_n (int): Number of top keywords to return. Defaults to 3.

        Returns:
            BlogBuilderState: Updated state with 'keywords' as a list of top nouns.
        """
        user_input = state.get("user_input", "")

        # Tokenize and POS tagging
        words = nltk.word_tokenize(user_input)
        pos_tags = nltk.pos_tag(words)

        stop_words = set(stopwords.words("english"))

        # Keep only nouns, exclude stopwords, and ignore single-character tokens
        nouns = [
            word.lower()
            for word, pos in pos_tags
            if pos.startswith("NN") and word.lower() not in stop_words and len(word) > 1
        ]

        # Frequency count
        noun_freq = Counter(nouns)
        keywords = [word for word, _ in noun_freq.most_common(top_n)]

        state["keywords"] = keywords
        return state
