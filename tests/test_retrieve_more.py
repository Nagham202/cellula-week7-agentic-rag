
from src.analyst.analyst_agent import analyst_agent


def test_retrieve_more_through_agent():
    result = analyst_agent.invoke({
        "messages": [{
            "role": "user",
            "content": """
            Use the retrieve_more_evidence tool to find information
            about the accuracy results of RAG.

            Retrieve up to 4 relevant chunks and summarize the findings.
            """
        }]
    })

    print("\nAnalyst Agent response:")
    print(result["messages"][-1].content)
