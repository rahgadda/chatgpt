import gradio as gr
from weaviate.client import Client

############################
### Variable Declaration ###
############################

# -- UI Variables
# Product
ui_product_name=gr.Textbox(placeholder="Product Name, OFSLL",label="Product Name")
ui_product_description=gr.Textbox(placeholder="Product Desc, Oracle Financial Lending and Leasing",label="Product Description")
ui_product_prompt=gr.Textbox(placeholder="Prompt,what {text} w.r.t OFSLL",label="Prompt")
ui_product_um=gr.UploadButton("Upload User Manual", file_types=[".pdf"])
ui_product_mapping=gr.UploadButton("Upload Mapping Excel", file_types=[".xlsx"])

# Env Variables
ui_api_key=gr.Textbox(placeholder="OpenAI API Key, sk-XXX",label="OpenAI API Key")
ui_weaviate_url=gr.Textbox(placeholder="Weaviate URL, https://weaviate.xxx",label="Weaviate URL")

# Output
ui_output=gr.Textbox(lines=22,label="Output")


# -- Placeholder Variables
p_inputs = [
                ui_api_key,
                ui_weaviate_url,
                ui_product_name,
                ui_product_description,
                ui_product_prompt,
                ui_product_um,
                ui_product_mapping
           ]

# -- Global variables
g_openai_api_key=""
g_product_name=""
g_product_description=""
g_product_prompt=""
g_output=""
g_weaviate_url=""
g_client=None

############################
###### Generic Code #######
############################

# -- Updating global variables
def update_global_variables(ui_api_key, ui_weaviate_url, ui_product_name, ui_product_description, ui_product_prompt):
    global g_openai_api_key
    global g_weaviate_url
    global g_product_name
    global g_product_description
    global g_product_prompt
    global g_output

    # Reset values to defaults
    g_openai_api_key=""
    g_weaviate_url=""
    g_product_name=""
    g_product_description=""
    g_product_prompt=""

    print("started function - update_global_variables")

    try:
        # Setting g_openai_api_key
        if ui_api_key != "":
            print('Setting g_openai_api_key - '+ui_api_key)
            g_openai_api_key=ui_api_key
            g_output=g_output+'Setting g_openai_api_key - '+ui_api_key
        else:
            print("exception in function - update_global_variables")
            raise ValueError('Required OpenAI API Key')

        # Setting g_weaviate_url
        if ui_weaviate_url != "":
            print('Setting g_weaviate_url - '+ui_weaviate_url)
            g_weaviate_url=ui_weaviate_url
            g_output=g_output+'\nSetting g_weaviate_url - '+ui_weaviate_url
        else:
            print("exception in function - update_global_variables")
            raise ValueError('Required Weaviate VectorDB URL')

        # Setting g_product_name
        if ui_product_name != "":
            print('Setting g_product_name - '+ui_product_name)
            g_product_name=ui_product_name
            g_output=g_output+'\nSetting g_product_name - '+ui_product_name
        else:
            print("exception in function - update_global_variables")
            raise ValueError('Required Product Name')

        # Setting g_product_description
        if ui_product_description != "":
            print('Setting g_product_description - '+ui_product_description)
            g_product_description=ui_product_description
            g_output=g_output+'\nSetting g_product_description - '+ui_product_description
        else:
            print("exception in function - update_global_variables")
            raise ValueError('Required Product Description')

        # Setting g_product_prompt
        if ui_product_prompt != "":
            print('Setting g_product_prompt - '+ui_product_prompt)
            g_product_prompt=ui_product_prompt
            g_output=g_output+'\nSetting g_product_prompt - '+ui_product_prompt
        else:
            print("No prompting specified")
            g_output=g_output+'\nNo values set for g_product_prompt'

    finally:
        print("completed function - update_global_variables")

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

# -- Convert input to CamelCase
def convert_to_camel_case(string):
    words = string.split('_')
    camel_case_words = [word.capitalize() for word in words]
    return ''.join(camel_case_words)

# -- Create OpenAI Embedding
def create_openai_embeddings(text):
    print("Creating embedding for text"+ text)

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
##### Create Product DB ####
############################

# -- Check for Product Class/Table
def create_product_class():
    global g_client
    global g_output

    print("started function - create_product_class")

    # Define the class "Product" with properties name,description
    product_class = {
                        "classes": [{
                            "class": "Product",
                            "description": "Store Product Names and Description",
                            "vectorizer": "none",
                            "properties": [
                                {
                                    "name": "name",
                                    "dataType": ["text"],
                                    "description": "Product Name"
                                },
                                {
                                    "name": "description",
                                    "dataType": ["text"],
                                    "description": "Product Description"
                                },
                                {
                                    "name": "prompt",
                                    "dataType": ["text"],
                                    "description": "Prompt variable to store mapping description. This is non-mandatory"
                                }, 
                                {
                                    "name": "um_indicator",
                                    "dataType": ["text"],
                                    "description": "Indicator to check in User Manual exist"
                                }   
                            ]
                        }]
                    }

    # Create the class in Weaviate
    try:
        response = g_client.schema.create(product_class)
        g_output=g_output+"Class 'Product' created successfully!\n"
        print("Class 'Product' created successfully!")
    except Exception as e:
        g_output=g_output+f"Failed to create class 'Product': {e}"+"\n"
        print(f"Failed to create class 'Product': {e}")
    finally:
        print("completed function - create_product_class")

# -- Check for Product Object/Row
def validate_product_object_exist():
    global g_client
    global g_product_name
    global g_output

    print("started function - validate_product_object_exist")

    # Check if data exists based on input - product_name  
    where_filter = {
                        "path": ["name"],
                        "operator": "Equal",
                        "valueString": g_product_name
                   }

    query_result = (
                        g_client.query
                        .get("Product", "name")
                        .with_where(where_filter)
                        .do()
                   )
    
    print("Product Table Query Result - "+str(query_result))
    if len(query_result['data']['Get']['Product']) == 0:
        g_output=g_output+"Product object does not exists\n"
        print("completed function - validate_product_object_exist")
        return True
    else:
        g_output=g_output+"Product object already exists\n"
        print("completed function - validate_product_object_exist")
        return False

# -- Create new Product Object/Row
def create_new_product_object():
    global g_client
    global g_product_name
    global g_product_description
    global g_product_prompt
    global g_output

    print("started function - create_new_product_object")
    try:
        data_object =   {
                            "name": g_product_name,
                            "description": g_product_description,
                            "prompt": g_product_prompt,
                            "um_indicator": 'N'
                        }

        g_client.data_object.create(data_object, class_name="Product")
        print("Product object Created Successfully")
        g_output=g_output+"Product object Created Successfully\n"
    except Exception as e:
        raise ValueError("Creating Product Object"+str(e))
    finally:
        print("completed function - create_new_product_object")

# -- Add Product Object/Row
def add_product_data():
    global g_product_name
    global g_product_description
    global g_client
    global g_output

    print("started function - add_product_data")

    # -- Check if Product Table Exist
    try:
        g_client.schema.get("Product")
        print("Class 'Product' already exists!")
        g_output=g_output+"Class 'Product' already exists!\n"
    except Exception as e:
        print(f"Error Verifying Class Product : {e}")
        create_product_class()

    # -- Check & Create new Product Object
    if validate_product_object_exist():
       create_new_product_object() 
    
    print("completed function - add_product_data")

############################
##### Create Product UM ####
############################

# -- Check for User Manual Class/Table
def create_um_class():
    None

# -- Check for User Manual Object/Row
def validate_um_object_exist():
    None

# -- Create new User Manual Object/Row
def create_new_um_object():
    None

# -- Process User Manual
def process_um_data():
    None

############################
#### Create Product Map ####
############################

# -- Check for Mapping Class/Table
def create_mapping_class():
    None

# -- Check for Mapping Object/Row
def validate_mapping_object_exist():
    None

# -- Create new Mapping Object/Row
def create_new_mapping_object():
    None

# -- Process Mapping Excel Data
def process_mapping_data():
    None

############################
###### Submit Button #######
############################

# -- On Click of Submit Button in UI
def submit(ui_api_key, ui_weaviate_url, ui_product_name, ui_product_description, ui_product_prompt, ui_product_um, ui_product_mapping):
    global g_output

    print("\n>>> Started Training <<<")
    g_output=""
    
    if ui_api_key != "" or ui_product_name != "" or ui_product_description != "":
        try:
            # Setting Global Variables
            g_output=">>> 1 - Setting Variables <<<\n"
            print(">>> 1 - Setting Variables <<<")
            update_global_variables(ui_api_key, ui_weaviate_url, ui_product_name, ui_product_description, ui_product_prompt)
            g_output=g_output+"\n>>> 1 - Completed <<<\n"
            print(">>> 1 - Completed <<<\n")

            # Validate Weaviate Connection
            g_output=g_output+"\n>>> 2 - Validate Weaviate Connection <<<\n"
            print(">>> 2 - Validate Weaviate Connection <<<")
            weaviate_client()
            g_output=g_output+"\n>>> 2 - Completed <<<\n"
            print(">>> 2 - Completed <<<\n")

            # Create Product Class & Object
            g_output=g_output+"\n>>> 3 - Create Product Class & Object <<<\n"
            print(">>> 3 - Create Product Class & Object <<<")
            add_product_data()
            g_output=g_output+">>> 3 - Completed <<<\n"
            print(">>> 3 - Completed <<<\n")

        except Exception as e:
            print(">>> Completed Training <<<\n")
            return g_output+"Error -> " + str(e)
    else:
        print(">>> Completed Training <<<\n")
        g_output="Welcome to Migration Assistance Training Bot !!!\n" \
               "Enter input value to proceed"

    return g_output

# -- Start of Program - Main
def main():
    global p_inputs
    global ui_output

    interface=gr.Interface(
                        fn=submit,
                        inputs=p_inputs,
                        outputs=ui_output,
                        allow_flagging="never"
                    )
    interface.launch()

# -- Calling Main Function
if __name__ == '__main__':
    main()