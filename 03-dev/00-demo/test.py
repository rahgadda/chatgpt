import gradio as gr

g_ui_output = []

def my_function(dropdown_value: gr.Dropdown) -> gr.Dropdown :
    global g_ui_output

    if dropdown_value == 'Option 1':
        g_ui_output = ['Option 2', 'Option 3']
    elif dropdown_value == 'Option 2':
        g_ui_output = ['Option 3', 'Option 4']
    else:
        g_ui_output = ['Option 4', 'Option 1']
    
    # Update ui_output with new values from g_ui_output
    ui_output.update(g_ui_output)

    print("Values - ")
    print(g_ui_output)

    return gr.Dropdown.update(
            choices=g_ui_output, value=g_ui_output[1]
        )

# Create the gradio block layout.
with gr.Blocks() as demo:
    ui_input=gr.Dropdown(["Option 1","Option 2"], label="Updated dropdown values")
    ui_output=gr.Dropdown([], label="Updated dropdown values", interactive=True)

    ui_input.change(
        fn=my_function,
        inputs=[ui_input],
        outputs=[ui_output]
    )

# Run the gradio app.
demo.launch()