import gradio as gr


def greet(textbox: gr.Textbox,chatbot):
    chatbot.append((textbox,"Hello "+textbox))
    return chatbot,""

with gr.Blocks() as demo:
    # Adding components
    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=450)
    textbox = gr.Textbox()
    button = gr.Button("Greet")

    # Adding events
    button.click(fn=greet, inputs=[textbox,chatbot], outputs=[chatbot,textbox])

    demo.queue().launch()