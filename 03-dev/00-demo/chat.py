import gradio as gr
import tempfile
import openai
from openai.embeddings_utils import get_embedding
from weaviate.client import Client

############################
### Variable Declaration ###
############################

# -- Global Variables
g_product_details={}
g_client=None
g_weaviate_url=""
g_openai_api_key=""
openai

def update_global_variables(ui_api_key,ui_weaviate_url,chatbot):
    global g_openai_api_key
    global g_weaviate_url 
    global openai   

    # Reset values to defaults
    g_openai_api_key=""
    g_weaviate_url=""
    chatbot.clear()

    # Loading global variables
    chatbot.append((None,"Loading Parameters, API Key & Weaviate URL"))
    
    # Validation for OpenAI Key
    if ui_api_key != "":
        print('Setting g_openai_api_key - '+ui_api_key)
        g_openai_api_key=ui_api_key
        openai=g_openai_api_key
        chatbot.append((None,"Updated OpenAI API Key"))
    else:
        print('Required OpenAI API Key')
        chatbot.append((None,"<b style='color:red'>Required OpenAI API Key</b>"))

    # Validation for Weaviate URL
    if ui_weaviate_url != "":
        print('Setting g_weaviate_url - '+ui_weaviate_url)
        g_weaviate_url=ui_weaviate_url
        weaviate_client()
        chatbot.append((None,"Updated Weaviate URL"))
    else:
        print('Required Weaviate URL')
        chatbot.append((None,"<b style='color:red'>Required Weaviate URL</b>"))

    # Load Product Details
    update_products_list()

    return chatbot

############################
###### Generic Code #######
############################

# -- Create Weaviate Connection
def weaviate_client():
    global g_client
    global g_weaviate_url

    try:
        g_client = Client(url=g_weaviate_url, timeout_config=(3.05, 9.1))
        print("Weaviate client connected successfully!")
    except Exception as e:
        print("Failed to connect to the Weaviate instance."+str(e))
        raise ValueError('Failed to connect to the Weaviate instance.')

# -- Convert input to CamelCase
def convert_to_camel_case(string):
    words = string.split('_')
    camel_case_words = [word.capitalize() for word in words]
    return ''.join(camel_case_words)

# -- Create OpenAI Embedding
def create_openai_embeddings(text):
    # print("Creating embedding for text"+ text)

    # Updating Embedding
    retry_attempts = 3
    retry_interval = 65

    # Create OpenAI embeddings
    for attempt in range(retry_attempts):
        try:
            embedding = get_embedding(text, engine="text-embedding-ada-002")
            return embedding
        except Exception as e:
            time.sleep(retry_interval)
            print(str(e))

############################
##### Search Product DB ####
############################

# -- Get Product Codes in Lov
def update_products_list():
    global g_client
    global g_product_details

    print("started function - update_products_list")

    try:
        api_response = g_client.query.get("Product", ["name","description"]).do()
        print("Product API Response")
        print(api_response)
        g_product_details = api_response['data']['Get']['Product']
        product_details = [d["name"] for d in g_product_details]
        print("Product API Response")
        print(product_details)
    except Exception as e:
        print("Error getting Product Details")
    finally:
        print("completed function - update_products_list")

# -- Start of Program - Main
def main():
    print("\nStarted Knowledge Base Chat Application")

    with gr.Blocks() as demo:
        with gr.Accordion("Settings"):
            ui_api_key=gr.Textbox(placeholder="OpenAI API Key, sk-XXX",label="OpenAI API Key")
            ui_weaviate_url=gr.Textbox(placeholder="Weaviate URL, https://weaviate.xxx",label="Weaviate URL")

        chatbot = gr.Chatbot([], elem_id="chatbot").style(height=450)

        with gr.Row():
            with gr.Column(scale=0.2, min_width=0):
                action_dropdown = gr.Dropdown(
                    ["Query","Update"],
                    label="Action Type"
                )
            with gr.Column(scale=0.2, min_width=0):
                product_dropdown = gr.Dropdown(
                    ["OFSLL"],
                    label="Select Product"
                )
            with gr.Column(scale=0.6):
                txt = gr.Textbox(
                    show_label=False,
                    interactive=True,
                    lines=3.2,
                    placeholder="Message me, I am your migration assistance",
                ).style(container=False)
            
            # Loading global variables
            action_dropdown.change(
                                    fn=update_global_variables,
                                    inputs=[ui_api_key,ui_weaviate_url,chatbot],
                                    outputs=[chatbot]
                                  )
    
    demo.queue().launch(server_name="0.0.0.0")

# -- Calling Main Function
if __name__ == '__main__':
    main()