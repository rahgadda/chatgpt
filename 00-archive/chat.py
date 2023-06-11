import os
import time
import re
import requests
import gradio as gr
import openai
from openai.embeddings_utils import get_embedding
from dotenv import load_dotenv
from weaviate.client import Client

product_name=None
product_desc=None

weaviate_url=""
openai

############################
###### Generic Code #######
############################

# Generate HTML Table
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
    </table></br></br>
    """

    return html_table

# Convert text to paragraph
def convert_to_html_paragraph(text):
    html_paragraph =  "<p>" + text.replace('\n', ' ') + "</p>"
    return html_paragraph

# Generate HTML Response
def generate_html_response(um_data, openai_data, table_data):
    
    # Converting text to paragraph 
    um_data = convert_to_html_paragraph(um_data)
    openai_data = convert_to_html_paragraph(openai_data)
    table_data = convert_to_html_table(table_data)
    
    response = f"""
    <!DOCTYPE html>
    <html>
    <body>
      <h1 style='color:green'><b>Mapping Suggestion</b></h1>
        {table_data}
        
     
      <h1 style='color:green'><b>AI Suggestion</b></h1>
      <div>
        {openai_data}
      </div></br></br>
        
      <h1 style='color:green'><b>User Manual</b></h1>
      <div>
        {um_data}
      </div>

    </body>
    </html>
    """

    return response

# Initialized weaviate socket
def weaviate_client():
    global client

    try:
        client = Client(url=weaviate_url, timeout_config=(3.05, 9.1))
        print("Weaviate client connected successfully!")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the Weaviate instance.")

# Load Environment Variables
def load_env_variables():
    global weaviate_url
    global openai

    load_dotenv()
    openai.api_key=os.getenv("OPENAI_API_KEY")
    weaviate_url=os.getenv("WEAVIATE_URL")
    weaviate_client()
    
    print('\n##########################################################')
    print('>>>>>>>>>>>>>  Displaying Environment Variables <<<<<<<<<<')
    print('##########################################################')
    print('Loaded OpenAI API Key     -> '+os.getenv("OPENAI_API_KEY"))
    print('Loaded Weaviate URL       -> '+os.getenv("WEAVIATE_URL"))
    print('##########################################################\n')

# Convert to CamelCase
def convert_to_camel_case(string):
    words = string.split('_')
    camel_case_words = [word.capitalize() for word in words]
    return ''.join(camel_case_words)

# Create OpenAI Embedding
def create_openai_embeddings(text):
    print("Creating embedding for text "+ text)

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
###### Dropdown Change #####
############################

# Get Product Codes in Lov
def get_product_code_lov():
    api_response = client.query.get("Product", ["name"]).do()
    product_names = [product['name'] for product in api_response['data']['Get']['Product']]
    print("Loading Product List API response:")
    print(api_response)
    return product_names

# Get Product Description with Code
def get_product_desc(product_code):
    where_filter = {
                        "path": ["name"],
                        "operator": "Equal",
                        "valueString": product_code
                    }
    
    api_response = (
                        client.query
                        .get("Product", "description")
                        .with_where(where_filter)
                        .do()
                    )
    product_description = [product['description'] for product in api_response['data']['Get']['Product']]
    print(api_response)
    return product_description[0]

# Change Product Lov will replace history
def change_product(history, dropdown):
    global product_name
    global product_desc

    if dropdown:
        history=""
        product_name=dropdown
        product_desc=get_product_desc(dropdown)
        
        print("\nGetting Product Name OnChange:")
        print(dropdown)
        print("Getting Product Descriptions OnChange:")
        print(product_desc)

############################
###### Text Prompting ######
############################
    
# User Manual Data
def search_um(text,input_embedding):
    um_data = "No results from User Manual"
    vector = {"vector": input_embedding}
    
    if product_name:
        response = client \
            .query.get(convert_to_camel_case(product_name+"_um"), ["content", "_additional {certainty}"]) \
            .with_near_vector(vector) \
            .with_limit(1) \
            .do()
        # print(result)
        if response:
            result = response['data']['Get']['OfsllUm'][0]['content']
            result_value = result.split('\nResult : ')[0]
            um_data = result_value
    else:
        um_data = "Please select product name to proceed"
    
    return um_data

# OpenAI Data
def search_openAI(text):
    if product_name:
        text="what is "+text+" w.r.t Oracle Financials Lending and Leasing"
        # Generate text using the OpenAI model
        response = openai.Completion.create(
                                                engine='text-davinci-003',
                                                prompt=text,
                                                max_tokens=4000
                                            )
        
        openai_data = response.choices[0].text.strip()
        return openai_data
    else:
        return "Please select product name to proceed"

# Mapping Data
def generic_search_mapping_data(text):
    global product_name

    print("Performing Generic Search")
    
    where_product_name = convert_to_camel_case(product_name+"_mapping")
    
    where_filter = {
                        "path": ["key"],
                        "operator": "Like",
                        "valueString": text
                    }
    
    api_response = (
                        client.query
                        .get(where_product_name, "key, description")
                        .with_where(where_filter)
                        .do()
                    )
    try:
        first_key_value = api_response['data']['Get']['OfsllMapping'][0]['key']
        first_desc = api_response['data']['Get']['OfsllMapping'][0]['description']
        
        print("Generic Response ->")
        print(first_key_value)
        print(first_desc)
        return {
                    'input': text,
                    'key':first_key_value,
                    'description': first_desc,
                    'certainty': "0.9"
                }
    except Exception as e:
        return None        
    
def semantic_search_mapping_data(text,input_embedding):
    global product_name
    
    print("Performing Semantic Search")

    where_product_name = convert_to_camel_case(product_name+"_mapping")
    vector = {"vector": input_embedding}
    result = client \
            .query.get(where_product_name, ["key","description", "_additional {certainty}"]) \
            .with_near_vector(vector) \
            .with_limit(1) \
            .do()
    
    print("Semantic Response ->")
    print(result)

    ofsll_mapping = result['data']['Get'].get('OfsllMapping')

    if ofsll_mapping:
        for item in ofsll_mapping:
            key = item['key']
            description = item['description']
            certainty = item['_additional']['certainty']
            
            print("Key:", key)
            print("Description:", description)
            print("Certainty:", certainty)

            return {
                    'input': text,
                    'key':key,
                    'description': description,
                    'certainty': certainty
                   }
    else:
        print("OfsllMapping has no data.")
        return {
                    'input': text,
                    'key': None,
                    'description': None,
                    'certainty': None
                }

def hybrid_search_mapping_data(text,input_embedding):

    print("Performing Hybrid Search")

    if product_name:
        generic_search_response = generic_search_mapping_data(text)

        if generic_search_response:
            return generic_search_response
        else:
            return semantic_search_mapping_data(text,input_embedding)
    else:
        return {
                    'input': text,
                    'key': None,
                    'description': None,
                    'certainty': None
                }

# Text Prompt
def add_text(history, text):
    print("User Input :"+text)
    
    input_embedding=create_openai_embeddings(text)

    bot_response=generate_html_response(search_um(text,input_embedding),search_openAI(text),hybrid_search_mapping_data(text,input_embedding))
    history = history + [(text, bot_response)]
    return history,""

############################
######## Sample Code ######
############################

# Upload Sample and Generate label xlsx
def add_sample_file(history, file):
    history = history + [((file.name,), None)]
    return history

# Sample File Confirmation Message
def confirmation_sample_file(history):
    history = history + [(None, "Processing of sample file Completed")]
    return history

############################
######## Mapping Code ######
############################

# Upload labels and get mapping xlsx
def add_mapping_file(history, file):
    history = history + [((file.name,), None)]
    return history

# Mapping Confirmation Message
def confirmation_mapping_file(history):
    history = history + [(None, "Processing Mapping data Completed")]
    return history

############################
######### Main Code ########
############################

# Start of Program - Main
def main():
    print("\nStarted Knowledge Base Chat Application")
    load_env_variables()
    
    # Designing Chatbot UI
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot([], elem_id="chatbot").style(height=750)
        
        with gr.Row():
            with gr.Column(scale=0.2, min_width=0):
                dropdown = gr.Dropdown(
                    get_product_code_lov(),
                    label="Select Product"
                )
            with gr.Column(scale=0.65):
                txt = gr.Textbox(
                    show_label=False,
                    placeholder="Message me, I am your migration assistance",
                ).style(container=False)
            with gr.Column(scale=0.075, min_width=0):
                btn_sample = gr.UploadButton("📊", file_types=[".xlsx"])
            with gr.Column(scale=0.075, min_width=0):
                btn_mapping = gr.UploadButton("📊", file_types=[".xlsx"])
        
        txt.submit(add_text, [chatbot, txt], [chatbot, txt])
        btn_sample.upload(add_sample_file, [chatbot, btn_sample], [chatbot]).then(
            confirmation_sample_file, chatbot, chatbot
        )
        btn_mapping.upload(add_mapping_file, [chatbot, btn_mapping], [chatbot]).then(
            confirmation_mapping_file, chatbot, chatbot
        )
        dropdown.change(change_product, [chatbot, dropdown], [chatbot])

    demo.launch(server_name="0.0.0.0")

if __name__ == '__main__':
    main()


