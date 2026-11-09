from src.analyst.analyst_agent import analyst_agent

result = analyst_agent.invoke({
    "messages": [{
        "role": "user",
        "content": "Use the data analysis tool to analyze these numbers: 80, 90, 100. Give me the mean and median."
    }]
})

print(result["messages"][-1].content)