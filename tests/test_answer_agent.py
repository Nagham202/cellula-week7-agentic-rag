from src.answer.answer_agent import ERROR_MESSAGE, build_user_message, generate_answer
from src.answer.formatters import NOT_FOUND_MESSAGE

EVIDENCE = [
    {"source": "kito_manual.pdf", "page": 1, "text": "Full charge time: 90 minutes at the Kito Dock."},
    {"source": "nova_faq.txt", "page": None, "text": "Nova robots have a 2 year warranty."},
]


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


def test_message_has_numbered_evidence():
    message = build_user_message("How long?", "About 90 minutes.", EVIDENCE)
    assert "[1] kito_manual.pdf, page 1\nFull charge time" in message
    assert "[2] nova_faq.txt\nNova robots" in message


def test_answer_gets_its_sources():
    llm = FakeLLM("Kito charges in about 90 minutes [1].")
    result = generate_answer("How long?", "About 90 minutes.", EVIDENCE, llm=llm)
    assert result["sources"] == ["kito_manual.pdf, page 1"]
    assert "[kito_manual.pdf, page 1]" in result["answer"]


def test_strange_brackets_are_fixed():
    llm = FakeLLM("Kito charges in about 90 minutes at the Kito Dock【1】.")
    result = generate_answer("How long?", "About 90 minutes.", EVIDENCE, llm=llm)
    assert result["answer"].startswith("Kito charges in about 90 minutes at the Kito Dock [kito_manual.pdf, page 1].")
    assert result["sources"] == ["kito_manual.pdf, page 1"]


def test_not_found_has_no_sources():
    result = generate_answer("Capital of France?", "Not in the documents.", EVIDENCE, llm=FakeLLM("NOT_FOUND"))
    assert result == {"answer": NOT_FOUND_MESSAGE, "sources": []}


def test_no_evidence_does_not_call_the_model():
    llm = FakeLLM("should not be used")
    result = generate_answer("Capital of France?", "No relevant evidence was found.", [], llm=llm)
    assert result == {"answer": NOT_FOUND_MESSAGE, "sources": []}
    assert llm.received_messages is None


def test_model_error_gives_error_message():
    llm = FakeLLM(error=RuntimeError("all providers are down"))
    result = generate_answer("How long?", "About 90 minutes.", EVIDENCE, llm=llm)
    assert result == {"answer": ERROR_MESSAGE, "sources": []}
