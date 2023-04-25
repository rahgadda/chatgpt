import gradio as gr

def helloworld(name):
  return "Hello World -> "+name+"!!!"

interface = gr.Interface(fn=helloworld, inputs=["file","file","file"], outputs="file")
interface.launch()