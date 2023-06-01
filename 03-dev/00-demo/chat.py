import gradio as gr
import tempfile
import openai
from openai.embeddings_utils import get_embedding
from weaviate.client import Client
import time

############################
### Variable Declaration ###
############################

# -- Global Variables
g_product_details={}
g_client=None
g_weaviate_url=""
g_openai_api_key=""
openai

def update_global_variables(ui_api_key,ui_weaviate_url,ui_chatbot):
    global g_openai_api_key
    global g_weaviate_url 
    global openai   

    # Reset values to defaults
    g_openai_api_key=""
    g_weaviate_url=""
    ui_product_dropdown=gr.Dropdown.update(
                                            interactive=False
                                          )
    ui_chatbot.clear()

    # Loading global variables
    ui_chatbot.append((None,"Loading Parameters, API Key & Weaviate URL"))
    
    try:
        # Validation for OpenAI Key
        if ui_api_key != "":
            print('Setting g_openai_api_key - '+ui_api_key)
            g_openai_api_key=ui_api_key
            openai.api_key=g_openai_api_key
            ui_chatbot.append((None,"Updated OpenAI API Key"))
        else:
            print('Required OpenAI API Key')
            ui_chatbot.append((None,"<b style='color:red'>Required OpenAI API Key</b>"))

        # Validation for Weaviate URL
        if ui_weaviate_url != "":
            print('Setting g_weaviate_url - '+ui_weaviate_url)
            g_weaviate_url=ui_weaviate_url
            weaviate_client()
            ui_chatbot.append((None,"Updated Weaviate URL"))
            
            # Load Product Details
            update_products_variable()
            ui_product_dropdown = update_products_lov()
        else:
            print('Required Weaviate URL')
            ui_chatbot.append((None,"<b style='color:red'>Required Weaviate URL</b>"))

    except Exception as e:
        print('Exception in loading parameters - '+str(e))
        ui_chatbot.append((None,"<b style='color:red'>Exception "+str(e)+"</b>"))
        raise ValueError(str(e))
    finally:
        return ui_chatbot,ui_product_dropdown

############################
###### Generic Code #######
############################

# -- Generate HTML Table
def convert_to_html_table(table_data):
    
    html_table = f"""
    <table style="border-collapse: collapse; width: 100%;">
        <tr>
            <th style="border: 1px solid black; text-align: center; padding: 8px;">Input</th>
            <th style="border: 1px solid black; text-align: center; padding: 8px;">Key</th>
            <th style="border: 1px solid black; text-align: center; padding: 8px;">Description</th>
            <th style="border: 1px solid black; text-align: center; padding: 8px;">Certainty</th>
        </tr>
        <tr>
            <td style="border: 1px solid black; text-align: center; padding: 8px;">{table_data['input']}</td>
            <td style="border: 1px solid black; text-align: center; padding: 8px;">{table_data['key']}</td>
            <td style="border: 1px solid black; text-align: center; padding: 8px;">{table_data['description']}</td>
            <td style="border: 1px solid black; text-align: center; padding: 8px;">{table_data['certainty']}</td>
        </tr>
    </table><br><br>
    """

    return html_table

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
    global openai

    # Updating Embedding
    retry_attempts = 3
    retry_interval = 65

    # Create OpenAI embeddings
    for attempt in range(retry_attempts):
        try:
            embedding = openai.embeddings_utils.get_embedding(text, engine="text-embedding-ada-002")
            return embedding
        except Exception as e:
            if "AuthenticationError" in str(e):
                raise ValueError("Creating Text Embedding")
            else:
                time.sleep(retry_interval)
                print(str(e))
    
    raise ValueError("Creating Text Embedding")

############################
## Update Product Details ##
############################

# -- Update Product LOV
def update_products_lov():
    global g_product_details

    print("started function - update_products_lov")
    product_details = [d["name"] for d in g_product_details]
    ui_product_dropdown = gr.Dropdown.update(
                                                choices=product_details, 
                                                value=product_details[0],
                                                interactive=True
                                            )
    print("completed function - update_products_lov")

    return ui_product_dropdown

# -- Get Product global variable
def update_products_variable():
    global g_client
    global g_product_details

    print("started function - update_products_variable")

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
        print("completed function - update_products_variable")

############################
#### Search User Manual ####
############################

def search_um(ui_search_text, ui_product_dropdown):
    um_data = "No results from User Manual"
    
    print("started function - search_um")
    print("Product Selected -->"+ui_product_dropdown)
    
    try:

        if ui_product_dropdown:
            input_embedding=create_openai_embeddings(ui_search_text)
            vector = {"vector": input_embedding}

            response = g_client \
                .query.get(convert_to_camel_case(ui_product_dropdown+"_um"), ["content", "_additional {certainty}"]) \
                .with_near_vector(vector) \
                .with_limit(1) \
                .do()
            
            # print(result)
            if response:
                result = response['data']['Get'][convert_to_camel_case(ui_product_dropdown+"_um")][0]['content']
                result_value = result.split('\nResult : ')[0]
                um_data = result_value
        else:
            um_data = "Please select product name to proceed"

        return um_data

    except Exception as e:
        raise ValueError(str(e))
    finally:
        print("completed function - search_um")

############################
#### Search Mapping Data ###
############################

def search_mapping_data(ui_search_text, ui_product_dropdown):
    um_data = "No results from Mapping Table"
    
    print("started function - search_mapping_data")
    print("Product Selected -->"+ui_product_dropdown)
    try:
        print("Performing Semantic Search")
        if ui_product_dropdown:
            input_embedding=create_openai_embeddings(ui_search_text)
            
            where_product_name = convert_to_camel_case(ui_product_dropdown+"_mapping")
            vector = {"vector": input_embedding}
            response = g_client \
                    .query.get(where_product_name, ["key","description", "_additional {certainty}"]) \
                    .with_near_vector(vector) \
                    .with_limit(1) \
                    .do()
            
            # print(result)
            if response:
                mapping = response['data']['Get'].get(convert_to_camel_case(ui_product_dropdown+"_mapping"))
                if mapping:
                    for item in mapping:
                        key = item['key']
                        description = item['description']
                        certainty = item['_additional']['certainty']
                        
                        print("Key:", key)
                        print("Description:", description)
                        print("Certainty:", certainty)

                        return {
                                'input': ui_search_text,
                                'key':key,
                                'description': description,
                                'certainty': certainty
                            }
                else:
                    print("Mapping has no data.")
                    return {
                                'input': ui_search_text,
                                'key': None,
                                'description': None,
                                'certainty': None
                            }

    except Exception as e:
        raise ValueError(str(e))
    finally:
        print("completed function - search_mapping_data")
    
############################
##### Search User Input ####
############################

def text_search(ui_product_dropdown, ui_search_text, ui_chatbot):
    
    print("started function - text_search")
    try:
        ui_chatbot.append((ui_search_text,None))
        um_search_results = search_um(ui_search_text, ui_product_dropdown)
        mapping_search_results = search_mapping_data(ui_search_text, ui_product_dropdown)
        
        ui_chatbot.append((None,"<b style='color:green'>Mapping Results: </b><br>"+convert_to_html_table(mapping_search_results)+"<b style='color:green'>User Manual Search Results: </b><br>"+um_search_results))
    except Exception as e:
        ui_chatbot.append((None,"<b style='color:red'>Exception "+str(e)+"</b>"))
    finally:
        print("completed function - text_search")
        return ui_chatbot

############################
##### Upload User Input ####
############################

def excel_file_search():
    None

############################
####### Main Program #######
############################

# -- Start of Program - Main
def main():
    print("\nStarted Knowledge Base Chat Application")

    with gr.Blocks() as demo:
        with gr.Accordion("Settings"):
            ui_api_key=gr.Textbox(placeholder="OpenAI API Key, sk-XXX",label="OpenAI API Key", type="password")
            ui_weaviate_url=gr.Textbox(placeholder="Weaviate URL, https://weaviate.xxx",label="Weaviate URL", type="password")

        ui_chatbot = gr.Chatbot([], elem_id="chatbot").style(height=450)

        with gr.Row():
            with gr.Column(scale=0.2, min_width=0):
                ui_action_dropdown = gr.Dropdown(
                    ["Query","Update"],
                    label="Action Type"
                )
            with gr.Column(scale=0.2, min_width=0):
                ui_product_dropdown = gr.Dropdown(
                    [],
                    interactive=False,
                    label="Select Product"
                )
            with gr.Column(scale=0.6):
                ui_search_text = gr.Textbox(
                    show_label=False,
                    # lines=3.2,
                    placeholder="Message me, I am your migration assistance",
                )

            # Loading global variables
            ui_action_dropdown.change(
                                    fn=update_global_variables,
                                    inputs=[ui_api_key,ui_weaviate_url,ui_chatbot],
                                    outputs=[ui_chatbot,ui_product_dropdown]
                                )

            # Search Text
            ui_search_text.submit(fn=text_search,
                                inputs=[ui_product_dropdown, ui_search_text, ui_chatbot],
                                outputs=[ui_chatbot]
                                )
            
    demo.launch(server_name="0.0.0.0")

# -- Calling Main Function
if __name__ == '__main__':
    main()