import gradio as gr

api_key=gr.Textbox(placeholder="OpenAI API Key, sk-XXX",label="OpenAI API Key")
product_name=gr.Textbox(placeholder="Product Name, OFSLL",label="Product Name")
product_description=gr.Textbox(placeholder="Product Desc, Oracle Financial Lending and Leasing",label="Product Description")
product_prompt=gr.Textbox(placeholder="Prompt,what {{text}} w.r.t OFSLL",label="Prompt")
product_um=gr.UploadButton("Upload User Manual", file_types=[".pdf"])
product_mapping=gr.UploadButton("Upload Mapping Excel", file_types=[".xlsx"])

output=gr.Textbox(lines=15,label="Output")

inputs=[
            api_key,
            product_name,
            product_description,
            product_prompt,
            product_um,
            product_mapping
      ]

def hello(api_key, product_name,product_description,product_prompt,product_um,product_mapping):
    print("entered here")
    return "HelloWorld"

interface=gr.Interface(fn=hello,inputs=inputs,outputs=output,allow_flagging="never")
interface.launch()