from src.analyst.analyst_agent import analyst_agent


def test_document_comparison_through_agent():
    result = analyst_agent.invoke({
        "messages": [{
            "role": "user",
            "content": """
            Use the document comparison tool to compare these two documents.

            Document A:
            Source: report_A.pdf
            Page: 2
            Content: The LSTM model achieved 90% accuracy and 88% F1 score.

            Document B:
            Source: report_B.pdf
            Page: 4
            Content: The BERT model achieved 95% accuracy and 93% F1 score.

            Compare their metrics and explain which model performed better.
            """
        }]
    })

    print(result["messages"][-1].content)
