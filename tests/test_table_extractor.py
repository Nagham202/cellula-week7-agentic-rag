from src.analyst.analyst_agent import analyst_agent


def test_table_extractor_through_agent():
    result = analyst_agent.invoke({
        "messages": [{
            "role": "user",
            "content": """
            Use the table extractor tool to extract this table:

            | Model | Accuracy | F1 |
            |-------|----------|----|
            | LSTM  | 90%      | 88% |
            | BERT  | 95%      | 93% |
            """
        }]
    })

    print(result["messages"][-1].content)