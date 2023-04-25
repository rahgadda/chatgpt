import gradio as gr

def helloworld(name):
  return "Hello World -> "+name+"!!!"

interface = gr.Interface(fn=helloworld, inputs="text", outputs="text")
interface.launch()