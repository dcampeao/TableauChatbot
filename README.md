# TableauChatbot
Using OpenAI API to allow natural language interaction with Tableau dashboards

This code was created in Databricks but it can also be run as a standalone python script. Just remove the magic commands and the dbutils.library.restartPython() command.

# Usage
Create an account with OpenAI, create a token and add it to the code client = OpenAI(api_key="",).

Replace the pre-existing prompt that describes the Superstore tabs with your dashboards' descriptions.

The result is a Gradio app running on local host. If the option shared=True is used on the launch command, a public link will also be created and hosted by hugging face.

# Limitations

This script was designed as a proof of concept and does not prevent the user from bypassing the initial instructions and using the model for other purposes.