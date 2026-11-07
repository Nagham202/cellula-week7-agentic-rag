from src.retriever.query_rewriter import build_user_message, parse_rewrite, rewrite_query


class FakeReply:
    def __init__(self, content):
        self.content = content


# acts like a langchain chat model without calling any api
class FakeLLM:
    def __init__(self, reply=None, error=None):
        self.reply = reply
        self.error = error
        self.received_messages = None

    def invoke(self, messages):
        self.received_messages = messages
        if self.error is not None:
            raise self.error
        return FakeReply(self.reply)


QUESTION = "What are its disadvantages?"


def test_valid_json_is_used():
    reply = '{"query": "What are the disadvantages of RAG?", "alternatives": ["What are the limits of RAG?"]}'
    result = rewrite_query(QUESTION, llm=FakeLLM(reply))
    assert result == {"query": "What are the disadvantages of RAG?",
                      "alternatives": ["What are the limits of RAG?"], "rewritten": True}


def test_json_inside_extra_text_or_code_fences_is_found():
    reply = 'Sure! Here it is:\n```json\n{"query": "Q", "alternatives": []}\n```'
    assert parse_rewrite(reply, QUESTION)["query"] == "Q"


def test_broken_replies_fall_back_to_the_original_question():
    for reply in ["no json here", '{"query": ""}', '{"alternatives": ["x"]}', "{not valid json}", '["a list"]']:
        assert parse_rewrite(reply, QUESTION) == {"query": QUESTION, "alternatives": [], "rewritten": False}


def test_alternatives_are_cleaned_and_limited_to_two():
    reply = '{"query": "Q", "alternatives": ["Q", "", 5, "A1", "A2", "A3"]}'
    assert parse_rewrite(reply, QUESTION)["alternatives"] == ["A1", "A2"]


def test_failed_llm_call_falls_back_to_the_original_question():
    result = rewrite_query(QUESTION, llm=FakeLLM(error=TimeoutError("all providers busy")))
    assert result["query"] == QUESTION
    assert result["rewritten"] is False


def test_history_keeps_last_three_turns_and_cuts_long_answers():
    history = []
    for number in range(1, 6):
        history.append({"role": "user", "content": f"question {number}"})
        history.append({"role": "assistant", "content": "x" * 1000})
    message = build_user_message(QUESTION, history)
    assert "question 1" not in message and "question 2" not in message
    assert "question 3" in message and "question 5" in message
    assert "x" * 401 not in message
    assert message.endswith(f"New question: {QUESTION}")


def test_no_history_is_written_as_none():
    assert build_user_message(QUESTION, None) == f"Conversation: (none)\nNew question: {QUESTION}"
