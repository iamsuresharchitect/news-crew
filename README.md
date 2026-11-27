# Two-Agent Crew for a Tech Newsletter

A small [CrewAI](https://www.crewai.com/) project where two agents work in a line:

- **Researcher** searches the web (SerpApi Google Search tool) and finds today's top 3 tech news stories.
- **Writer** has **no tools**. It works only from the Researcher's output and turns it into a 5-line newsletter.

Built for Week 4 / Day 4 of my GenAI learning track.

## How it works

```
Researcher (SerpApiGoogleSearchTool)  --context-->  Writer (no tools)
   finds top 3 stories + sources                      writes exactly 5 lines
```

- `Process.sequential`: the Researcher task runs first, then the Writer task.
- The Researcher's result is handed to the Writer explicitly with `context=[find]`. In a sequential crew the second task does not see the first one's output on its own.
- Only the Researcher has a tool. A Writer with a search tool would research again instead of writing.
- "5 lines" means: a title line, three story lines, and one "Why it matters" line.
- If search fails, the Writer reports "No story available" instead of inventing stories.

## Sample output (27 Nov 2026)

```
Tech in 5 lines
1. S&P put Nvidia's AA credit rating on CreditWatch negative, warning its board may be compromised after CEO Jensen Huang's departure and reinstatement, with a possible cut within about 90 days.
2. Bloomberg reports SAP is weighing at least 10,000 job cuts as part of an AI-driven restructuring.
3. Poland's defence ministry is set to sign a deal to buy Palantir's AI-powered software, despite domestic protests over the plan.
Why it matters: AI is now reshaping credit ratings, corporate workforces and military procurement, and each shift brings real risk, from governance and jobs to public backlash.
```

Screenshots of a full run (Researcher searching, then the Writer's output) are in [`news_crew_run.pdf`](news_crew_run.pdf).

## Setup

Requires Python 3.10+, an [Anthropic API key](https://console.anthropic.com/) and a [SerpApi key](https://serpapi.com/manage-api-key).

```bash
python -m venv venv

# activate the venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

pip install -r requirements.txt
# or: pip install 'crewai[tools,anthropic]' serpapi
```

Create a `.env` file next to `news_crew.py` (it is git-ignored):

```
ANTHROPIC_API_KEY=your-anthropic-key
SERPAPI_API_KEY=your-serpapi-key
MODEL=anthropic/claude-sonnet-5-5   # optional
```

## Run

```bash
python news_crew.py
```

Run it on different days and the stories change, because the Researcher searches live.

## Files

| File | Purpose |
|---|---|
| `news_crew.py` | The whole crew: 2 agents, 2 tasks, sequential process |
| `requirements.txt` | Python dependencies |
| `news_crew_run.pdf` | Screenshots of a full run |

## Stack

Python, CrewAI, crewai-tools (`SerpApiGoogleSearchTool`), Claude via the Anthropic API.

## Notes

- Keys are read from environment variables (loaded from `.env`). Never commit `.env`.
- The assignment suggested `SerperDevTool` (serper.dev). I used `SerpApiGoogleSearchTool` (serpapi.com) instead, since I had a SerpApi key.
