"""Two-agent CrewAI crew: Researcher (web search) -> Writer (no tools) -> 5-line tech newsletter.

Step 1 - Setup (folder + virtual environment):
    mkdir news_crew && cd news_crew
    python -m venv venv

    # activate the venv
    source venv/bin/activate          # macOS / Linux
    venv\\Scripts\\activate             # Windows (PowerShell / CMD)

    pip install 'crewai[tools,anthropic]' serpapi

    # keys: put them in a .env file next to this script (loaded automatically):
    #   ANTHROPIC_API_KEY=your-key
    #   SERPAPI_API_KEY=your-key      (key from serpapi.com/manage-api-key)
    # or set them in the shell instead:
    export ANTHROPIC_API_KEY="your-key"  # macOS / Linux
    export SERPAPI_API_KEY="your-key"
    export MODEL="anthropic/claude-sonnet-5-5"   # optional, defaults below

    $env:ANTHROPIC_API_KEY="your-key"    # Windows (PowerShell)
    $env:SERPAPI_API_KEY="your-key"
    $env:MODEL="anthropic/claude-sonnet-5-5"

Step 3 - Run:
    python news_crew.py
"""
import os
import sys
from datetime import date

from dotenv import load_dotenv  # installed with crewai
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import SerpApiGoogleSearchTool

# ---- Keys / model come from environment variables (loaded from .env if present) ----
load_dotenv(override=True)  # override=True so .env wins over stale/empty shell values
for key in ("ANTHROPIC_API_KEY", "SERPAPI_API_KEY"):
    if not os.environ.get(key):
        sys.exit(f"Missing environment variable: {key}")

MODEL = os.environ.get("MODEL", "anthropic/claude-sonnet-5-5")
llm = LLM(model=MODEL, api_key=os.environ["ANTHROPIC_API_KEY"])  # Claude via Anthropic API

today = date.today().strftime("%A, %d %B %Y")

# ---- Tool: only the Researcher gets it ----
search = SerpApiGoogleSearchTool()  # reads SERPAPI_API_KEY from the environment

# ---- Agents ----
researcher = Agent(
    role="Tech News Researcher",
    goal="Find the 3 most important technology news stories published today, using live web search.",
    backstory=(
        "You are a sharp tech journalist who scans the web every morning. "
        "You only report stories that are genuinely recent and from credible sources, "
        "and you never invent facts - everything comes from your search results."
    ),
    tools=[search],
    llm=llm,
    verbose=True,
)

writer = Agent(
    role="Newsletter Writer",
    goal="Turn researched tech stories into a crisp, exactly-5-line newsletter.",
    backstory=(
        "You are a newsletter editor known for tight, punchy writing. "
        "You cannot browse the web: you work only from the research notes you are handed "
        "and never add facts that are not in them."
    ),
    # No tools on purpose - otherwise it would go and research again instead of writing.
    llm=llm,
    verbose=True,
)

# ---- Tasks ----
find = Task(
    description=(
        f"Today is {today}. Search the web for today's top 3 technology news stories. "
        "Prefer stories from the last 24 hours and reputable outlets. "
        "For each story capture what happened and why it matters."
    ),
    expected_output=(
        "Exactly 3 stories as a numbered list. For each: a one-line headline, "
        "a one-sentence summary, and the source name + URL. No extra commentary."
    ),
    agent=researcher,
)

write = Task(
    description=(
        "Using ONLY the research notes from the previous task, write a short tech newsletter. "
        "Do not search or add outside facts. Each story gets a single line, followed by one "
        "'Why it matters' line that ties the three stories together."
    ),
    expected_output=(
        "Exactly 5 lines of plain text, nothing before or after, in this format:\n"
        "Line 1: Tech in 5 lines\n"
        "Line 2: 1. <first story, one line>\n"
        "Line 3: 2. <second story, one line>\n"
        "Line 4: 3. <third story, one line>\n"
        "Line 5: Why it matters: <one line>"
    ),
    agent=writer,
    context=[find],  # hands the Researcher's output to the Writer
)

# ---- Crew ----
crew = Crew(
    agents=[researcher, writer],
    tasks=[find, write],
    process=Process.sequential,
    verbose=True,
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n" + "=" * 40)
    print(result)
