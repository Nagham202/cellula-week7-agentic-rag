import tempfile
from pathlib import Path

import streamlit as st

from src.chat_graph import ask
from src.pipeline.ingest import ingest_file
from src.pipeline.loaders import SourceError
from src.pipeline.store import count_chunks, delete_source, list_sources

st.set_page_config(page_title="Chat with your documents")
st.title("Chat with your documents")

# the chat is kept here between reruns, oldest message first
if "messages" not in st.session_state:
    st.session_state.messages = []


def upload_files(files):
    # each file is saved with its real name, because the name becomes the source in the citations
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder:
        for file in files:
            path = Path(folder) / file.name
            path.write_bytes(file.getvalue())
            try:
                chunk_count = ingest_file(path)
                st.success(f"{file.name}: {chunk_count} chunks added")
            except SourceError as error:
                st.error(str(error))


with st.sidebar:
    st.header("Documents")
    files = st.file_uploader("Upload PDF, DOCX or TXT files", type=["pdf", "docx", "txt"],
                             accept_multiple_files=True)
    if files and st.button("Add to the knowledge base"):
        with st.spinner("Reading the files..."):
            upload_files(files)

    st.subheader("Stored files")
    for source in list_sources():
        name_column, button_column = st.columns([4, 1])
        name_column.write(f"{source} ({count_chunks(source)} chunks)")
        if button_column.button("Delete", key=f"delete_{source}"):
            delete_source(source)
            st.rerun()

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

# show the chat so far
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask a question about your documents")
if question:
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching and analyzing..."):
            # the history is passed before the new question is added to it
            reply = ask(question, st.session_state.messages)
        st.markdown(reply["answer"])
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": reply["answer"]})
