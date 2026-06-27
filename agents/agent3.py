import logging
import os
import re
import warnings
from pathlib import Path

from dotenv import load_dotenv

# Silence Firecrawl's Pydantic "field name shadows attribute" warnings before
# the SDK is imported anywhere in the process.
warnings.filterwarnings("ignore", message='Field name "json" in .* shadows an attribute')

from agentspan.agents import Agent, AgentRuntime, run, tool


load_dotenv(override=True)
logging.basicConfig(level=logging.WARNING, force=True)
logging.disable(logging.INFO)

MODES = {"sequential", "parallel", "nested", "worker"}
REPORTS_DIR = Path("reports")
MAX_PAGE_CHARS = 4000


@tool(credentials=["FIRECRAWL_API_KEY"])
def search_web(query: str, limit: int = 5) -> list[dict]:
    """Search the web with Firecrawl. Returns a list of {title, url, description}."""
    from firecrawl import Firecrawl

    fc = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
    response = fc.search(query, limit=limit)
    return [
        {"title": r.title or "", "url": r.url or "", "description": r.description or ""}
        for r in (response.web or [])
    ]


@tool(credentials=["FIRECRAWL_API_KEY"])
def fetch_page(url: str) -> str:
    """Fetch a web page as markdown via Firecrawl. Truncated for the LLM context."""
    from firecrawl import Firecrawl

    fc = Firecrawl(api_key=os.environ["FIRECRAWL_API_KEY"])
    document = fc.scrape(url, formats=["markdown"])
    markdown = document.markdown or ""
    return markdown[:MAX_PAGE_CHARS] if markdown else f"No content found at {url}."


researcher = Agent(
    name="researcher",
    model="openai/gpt-5.4",
    instructions=(
        "Research the topic thoroughly. Call search_web first, then fetch_page on "
        "the most relevant results. Write factual notes citing each claim. "
        "Always end your output with a '## Sources' section listing every URL you "
        "actually fetched, one per line, as markdown links: '- [title](url)'."
    ),
    tools=[search_web, fetch_page],
)

writer = Agent(
    name="writer",
    model="openai/gpt-5.4",
    instructions=(
        "Turn research notes into a clear, well-structured article. "
        "Preserve the '## Sources' section verbatim at the end."
    ),
)

editor = Agent(
    name="editor",
    model="openai/gpt-5.4",
    instructions=(
        "Polish the article for publication. Improve clarity and tighten writing. "
        "Do not modify or remove the '## Sources' section."
    ),
)