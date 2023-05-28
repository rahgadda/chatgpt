import gradio as gr

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
client=None

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
            g_output=g_output+'Setting g_product_prompt - '+ui_product_prompt
        else:
            print("No prompting specified")
            g_output=g_output+'\nNo values set for g_product_prompt'

    finally:
        print("completed function - update_global_variables")

# -- Create Weaviate Connection
def weaviate_client():
    global client

    try:
        client = Client(url=weaviate_url, timeout_config=(3.05, 9.1))
        print("Weaviate client connected successfully!")
    except requests.exceptions.ConnectionError:
        print("Failed to connect to the Weaviate instance.")

############################
##### Create Product DB ####
############################

############################
##### Create Product UM ####
############################

############################
#### Create Product Map ####
############################

# -- On Click of Submit Button in UI
def submit(ui_api_key, ui_weaviate_url, ui_product_name, ui_product_description, ui_product_prompt, ui_product_um, ui_product_mapping):
    global g_output

    print("\n>>> Started Training <<<")
    g_output=""
    
    if ui_api_key != "" or ui_product_name != "" or ui_product_description != "":
        try:
            # Setting Global Variables
            print(">>> 1 - Setting Variables <<<")
            update_global_variables(ui_api_key, ui_weaviate_url, ui_product_name, ui_product_description, ui_product_prompt)
            print(">>> 1 - Completed <<<")
        except Exception as e:
            print(">>> Completed Training <<<\n")
            return "Error -> " + str(e)
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