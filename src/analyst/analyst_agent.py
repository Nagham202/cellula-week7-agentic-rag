
from langchain.agents import create_agent

from src.llm import get_llm

from src.analyst.tools.calculator import calculator_tool
from src.analyst.tools.table_extractor import table_extractor_tool
from src.analyst.tools.document_comparison import document_comparison_tool
from src.analyst.tools.data_analysis import data_analysis_tool
from src.analyst.tools.retrieve_more import retrieve_more_evidence


llm = get_llm("analyst")


analyst_tools = [
    calculator_tool,
    table_extractor_tool,
    document_comparison_tool,
    data_analysis_tool,
    retrieve_more_evidence,
]


ANALYST_SYSTEM_PROMPT = """
You are an Analyst Agent in a document-based RAG system.

Your responsibilities:
- Analyze information retrieved from documents.
- Use the calculator for mathematical operations.
- Extract and analyze tables when needed.
- Compare information and metrics across documents.
- Calculate statistics and identify trends.
- Retrieve additional evidence when the provided evidence is insufficient.

Rules:
- Base your analysis on the provided document evidence.
- Do not invent facts, values, or results.
- Use the available tools when they are helpful.
- Clearly explain your findings.
- Mention when the evidence is insufficient.

- When requesting additional evidence, provide the IDs of
  previously retrieved chunks in already_seen_ids.
- Do not request additional evidence if the provided evidence
  is already sufficient.
"""


analyst_agent = create_agent(
    model=llm,
    tools=analyst_tools,
    system_prompt=ANALYST_SYSTEM_PROMPT
)
