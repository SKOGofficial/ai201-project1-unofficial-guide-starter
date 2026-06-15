import gradio as gr
from ingest import load_documents, chunk_document
from retriever import embed_and_store, retrieve, get_collection
from generator import generate_response


# ---------------------------------------------------------------------------
# Ingestion — runs once on startup
# ---------------------------------------------------------------------------

def run_ingestion():
    """
    Load hardware guide documents, chunk them, and store in ChromaDB.
    """
    collection = get_collection()

    if collection.count() > 0:
        print(f"Vector store already populated ({collection.count()} chunks). Skipping ingestion.")
        return

    print("Ingesting hardware guide documents...")
    documents = load_documents()
    all_chunks = []

    for doc in documents:
        chunks = chunk_document(doc["text"], doc["source"], doc["filename"], doc["extra_metadata"])
        all_chunks.extend(chunks)

    if all_chunks:
        embed_and_store(all_chunks)
        print(f"Ingestion complete. {len(all_chunks)} chunks stored.")


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

css = """
.main-container {
    max-width: 900px !important;
    margin: 0 auto !important;
    display: flex !important;
    flex-direction: column !important;
    height: 90vh !important;
}
.header-area {
    text-align: center;
    padding: 2rem 0;
    position: relative;
}
.refresh-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    min-width: 40px !important;
    padding: 5px !important;
}
.chatbot-container {
    flex-grow: 1 !important;
    overflow: hidden !important;
    display: flex !important;
    flex-direction: column !important;
}
footer {visibility: hidden}
"""

with gr.Blocks(
    theme=gr.themes.Soft(primary_hue="blue", spacing_size="sm", radius_size="md"),
    title="The Unofficial Guide",
    css=css
) as demo:

    # Top Right Refresh Button
    with gr.Row(elem_classes="header-area"):
        gr.HTML("""
            <h1 style="font-size:2.5rem; font-weight:800; color:#1e40af; margin:0; letter-spacing:-0.02em;">
                💻 The Unofficial Guide
            </h1>
            <p style="color:#6b7280; font-size:1.1rem; margin-top:0.5rem;">
                Modern Hardware Analysis & Recommendation Engine
            </p>
        """)
        refresh_btn = gr.Button("🔄", elem_classes="refresh-btn", variant="secondary")
        # Simple JavaScript to refresh the page
        refresh_btn.click(None, None, None, js="window.location.reload()")

    with gr.Column(elem_classes="chatbot-container"):
        chatbot = gr.Chatbot(
            show_label=False,
            container=True,
            height=500,
            type="messages",
            avatar_images=(None, "https://api.dicebear.com/7.x/bottts/svg?seed=HardwareExpert")
        )

        with gr.Row():
            # Example buttons container
            with gr.Column(scale=10):
                examples_ui = gr.Dataset(
                    components=[gr.Textbox(visible=False)],
                    label=None,
                    samples=[
                        ["What chip has the best single core performance?"],
                        ["Why do mini-PCs typically maintain higher sustained performance than laptops?"],
                        ["What architectural limitation does the OpenClaw guide highlight for Mac Mini?"],
                        ["Minimum memory footprint for 4-bit quantized Gemma 4 26B?"],
                        ["What platforms turn mini-PCs into homelab nodes in ServeTheHome series?"],
                    ],
                    type="values"
                )
            
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Ask about thermals, upgradeability, or TDP...",
                container=False,
                scale=7,
                show_label=False,
                autofocus=True
            )
            submit = gr.Button("Send", variant="primary", scale=1)

    # Logic to hide examples after first click and handle chat
    def user_msg(user_message, history):
        return "", history + [{"role": "user", "content": user_message}], gr.update(visible=False)

    def bot_res(history):
        user_message = history[-1]["content"]
        retrieved = retrieve(user_message)
        response = generate_response(user_message, retrieved)
        history.append({"role": "assistant", "content": response})
        return history

    msg.submit(user_msg, [msg, chatbot], [msg, chatbot, examples_ui], queue=False, show_api=False).then(
        bot_res, chatbot, chatbot, show_api=False
    )
    submit.click(user_msg, [msg, chatbot], [msg, chatbot, examples_ui], queue=False, show_api=False).then(
        bot_res, chatbot, chatbot, show_api=False
    )

    def load_example(example_data, history):
        return example_data[0], history

    examples_ui.click(load_example, [examples_ui, chatbot], [msg, chatbot], queue=False, show_api=False).then(
        user_msg, [msg, chatbot], [msg, chatbot, examples_ui], queue=False, show_api=False
    ).then(
        bot_res, chatbot, chatbot, show_api=False
    )


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  The Unofficial Guide — starting up")
    print("="*50 + "\n")
    run_ingestion()
    demo.launch()
