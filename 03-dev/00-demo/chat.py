import gradio as gr
import tempfile

############################
### Variable Declaration ###
############################

# -- Global Variables
g_product_details={}
g_client=None
g_weaviate_url=""
g_openai_api_key=""

def update_global_variables(ui_api_key,ui_weaviate_url,chatbot,txt):
    global g_openai_api_key
    global g_weaviate_url    

    # Reset values to defaults
    g_openai_api_key=""
    g_weaviate_url=""
    chatbot=[]
    chatbot.append(">>> Updating Parameters <<<\n")

    try:
        # Setting g_openai_api_key
        if ui_api_key != "":
            print('Setting g_openai_api_key - '+ui_api_key)
            g_openai_api_key=ui_api_key
            openai.api_key=g_openai_api_key
            chatbot.append('Setting g_openai_api_key - '+ui_api_key+"\n")
        else:
            print("exception in function - update_global_variables")
            chatbot.append('Required OpenAI API Key \n')

        # Setting g_weaviate_url
        if ui_weaviate_url != "":
            print('Setting g_weaviate_url - '+ui_weaviate_url)
            g_weaviate_url=ui_weaviate_url
            chatbot.append('Setting g_weaviate_url - '+ui_weaviate_url+"\n")
        else:
            print("exception in function - update_global_variables")
            chatbot.append('Required Weaviate VectorDB URL\n')
    finally:
        print("completed function - update_global_variables")
        chatbot.append(">>> Completed Parameters Update <<<\n")
        return chatbot

############################
###### Generic Code #######
############################

# -- Create Weaviate Connection
def weaviate_client():
    global g_client
    global g_output

    try:
        g_client = Client(url=g_weaviate_url, timeout_config=(3.05, 9.1))
        print("Weaviate client connected successfully!")
        g_output=g_output+"Weaviate client connected successfully!"
    except Exception as e:
        print("Failed to connect to the Weaviate instance."+str(e))
        raise ValueError('Failed to connect to the Weaviate instance.')
    finally:
        return g_output

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

def update_products_list():
    print("started function - update_products_list")
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
                    lines=3.2,
                    placeholder="Message me, I am your migration assistance",
                ).style(container=False)
            
            action_dropdown.change(
                                    fn=update_global_variables,
                                    inputs=[ui_api_key,ui_weaviate_url,chatbot,txt],
                                    outputs=[chatbot,txt]
                                  )
    
    demo.queue().launch(server_name="0.0.0.0")

# -- Calling Main Function
if __name__ == '__main__':
    main()