import asyncpg
from typing import Optional, List, Dict, Any


class PostgreSQL:
    """
    PostgreSQL database utility class for handling blog detail storage and retrieval.

    This class manages:
    - Connection lifecycle (connect/close)
    - Inserting processed blog details into the database
    - Searching blog analyses by topic or keyword
    """

    def __init__(self):
        """
        Initialize the PostgreSQL connection string from environment variables.

        Raises:
            ValueError: If the DATABASE_URL environment variable is not set.
        """
        self.connection_string: str = (
            "postgresql://joamps:tMtQNCKzgLicGU2AlBKh@echomind.c1c8wswwarpk.eu-west-2.rds.amazonaws.com:5432/echomind"
        )
        if not self.connection_string:
            raise ValueError(
                "❌ Postgres URI is missing. "
                "Set 'DATABASE_URL' in environment variables."
            )
        self.connection: Optional[asyncpg.Connection] = None

    async def connect(self) -> None:
        """
        Establish a connection to the PostgreSQL database.

        Raises:
            Exception: If unable to connect to the database.
        """
        try:
            self.connection = await asyncpg.connect(self.connection_string)
            print("✅ Connected to the database!")
        except Exception as e:
            print("❌ Error connecting to the database:", e)
            raise

    async def close(self) -> None:
        """
        Close the connection to the PostgreSQL database.

        Raises:
            Exception: If an error occurs while closing the connection.
        """
        try:
            if self.connection:
                await self.connection.close()
                print("🔒 Connection closed.")
        except Exception as e:
            print("❌ Error closing the connection:", e)

    async def insert_blog_details(
        self,
        session_id: str,
        title: Optional[str],
        topics: List[str],
        sentiment: str,
        summary: str,
        keywords: List[str],
    ) -> Optional[str]:
        """
        Insert a new record into the 'blog_details' table.

        Args:
            session_id (str): Unique session identifier (UUID or string).
            title (Optional[str]): Title of the blog (nullable).
            topics (List[str]): List of key topics extracted.
            sentiment (str): Sentiment label ("positive", "neutral", "negative").
            summary (str): Generated summary of the blog.
            keywords (List[str]): List of extracted keywords.

        Returns:
            Optional[str]: The session_id of the inserted row if successful, None otherwise.
        """
        try:
            await self.connect()

            insert_query = """
                INSERT INTO blog_details (
                    session_id, title, topics, sentiment, summary, keywords
                )
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING session_id;
            """

            result = await self.connection.fetchrow(
                insert_query,
                session_id,
                title,
                topics,
                sentiment,
                summary,
                keywords,
            )

            if result:
                print(f"✅ Inserted blog details for session {result['session_id']}")
                return result["session_id"]

        except Exception as e:
            print("❌ Error inserting blog details:", e)
            return None

        finally:
            await self.close()

    async def search_by_topic_or_keyword(self, topic: str) -> List[Dict[str, Any]]:
        """
        Search blog analyses by topic or keyword (case-insensitive).

        Args:
            topic (str): Search keyword (e.g., "AI", "fashion", "wellness").

        Returns:
            List[Dict[str, Any]]: A list of matching rows, each containing:
                - session_id (str)
                - title (str | None)
                - topics (List[str])
                - sentiment (str)
                - keywords (List[str])
                - summary (str)
        """
        try:
            await self.connect()

            query = """
                SELECT session_id, title, topics, sentiment, keywords, summary
                FROM blog_details
                WHERE 
                    LOWER($1) = ANY(ARRAY(SELECT LOWER(t) FROM unnest(topics) t)) 
                    OR LOWER($1) = ANY(ARRAY(SELECT LOWER(k) FROM unnest(keywords) k));
            """

            rows = await self.connection.fetch(query, topic)
            return [dict(row) for row in rows]

        except Exception as e:
            print("❌ Error searching:", e)
            return []

        finally:
            await self.close()
