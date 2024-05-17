# Databricks notebook source
# MAGIC %pip install gradio==3.27.0
# MAGIC %pip install openai

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

from openai import OpenAI
client = OpenAI(api_key="",)

# COMMAND ----------

import gradio as gr
import re
regex = "(?P<url>(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-]))"
initial_prompt = '''
I have Tableau dashboards with the following characteristics: [{'Name':'Profitability Overview', 
                                                                'Description':"Has information about a Supertore in United States including cards for: total sales, total profit, profit ratio, profit per order, profit per custumer, average discount and quantity. It also has a map showing for each unit a circle where it's size corresponds to the profit/loss and the color is blue if the profit ratio is positive and orange if it's negative. It has charts for Monthly Sales by segment and monthly sales by product category. It is possible to filter it by Order Date, Region (Central, East, South and West), State (All US States) and Profit Ratio.",
                                                                'url': 'https://public.tableau.com/views/Superstore_embedded_800x800/Overview'},
                                                                {'Name':'Product Drilldown', 
                                                                'Description': "It has a heatmap table where columns are calendar months and the rows are 2 index with product categories (Furniture, Office Supplies and Technology) and years. The values on the table are total sales. It also has a chart with the horizontal axis representing the total sales as dots, and 3 columns for the segment (Cosumer, Corporate and Home Office). The vertical axis has the product category and type of product. It is possible to filter it by Order Date, Region (Central, East, South and West), State (All US States), Profit and Profit Ratio.",
                                                                'url': 'https://public.tableau.com/views/Superstore_embedded_800x800/Product'},
                                                                {'Name':'On-Time Shipment Trends', 
                                                                'Description':"It shows the percentage or shippments late, on time and early. It also shows the number of days to ship by product in a gant chart where the horizontal axis is dates and the horizontal axis is the products. It is possible to filter it by Order Year, Order Quarter, Region and Ship Mode.",
                                                                'url': 'https://public.tableau.com/views/Superstore_embedded_800x800/Shipping'},
                                                                {'Name':'Sales Performance vs Target', 
                                                                 'Description':"It has a bar chart with the total sales for each procudt category as columns and a 2 index row with calendar month and segment. The bars are green when the sales are above target and orange when the sales are below target. It can be filtered by Year and Quarter.",
                                                                 'url': 'https://public.tableau.com/views/Superstore_embedded_800x800/Performance'},},
                                                                {'Name':'Order Details', 
                                                                 'Description':"It has a table at order level detail containing customer name, order date, ship date, ship mode, sale value, quantity, total profit, profit ratio, days to ship sheduled and actual. It can be filtered by Order Date, Region, State, City, Category and Segment.",
                                                                 'url': 'https://public.tableau.com/views/Superstore_embedded_800x800/OrderDetails'},},
                                                                ].
Based on the descriptions, respond the next prompt with the dashboard that most likely have the information requested. Make sure to include the url in your response so the user can access it but not as a link. If the region or state is mentioned in the question, add '?Region=Central' or '?State=California' to the url so the view can be filtered properly.
'''

message_history = [{"role": "user", "content":initial_prompt},{"role":"assistant", "content": 'Ok'}]

html = None

with gr.Blocks() as demo:
    with gr.Row() as row:
        with gr.Column(scale=1) as col:
            chatbot = gr.Chatbot()
            msg = gr.Textbox(lines=1)
            clear = gr.Button("Clear")
        with gr.Column(scale=2) as col:
            #Initialize the dashboard area with an empty space
            dashboard = gr.HTML(html)

    def user(user_message, history):
        return "", history + [[user_message, None]]

    def bot(history):
        global message_history
        #print(message_history)
        #print(history)
        message = history[-1][0]
        message_history.append({"role":"user", "content":message})
        completion = client.chat.completions.create(
            messages=message_history,
            model="gpt-3.5-turbo",
        )
        reply_content = completion.choices[0].message.content
        message_history.append({"role":"assistant", "content": reply_content})
        history[-1][1] = reply_content
        return history
    
    def update_dashboard(history):
        global html
        chatbot_response = history[-1][1]
        for part in chatbot_response.split():
            if 'public.tableau.com' in part:
                url = re.search(regex, part).group("url")
                print('url: ', url)
                html = '''
                <div class="tableauPlaceholder"">
                    <tableau-viz id="tableauViz" src='{url}' toolbar="bottom" hide-tabs>
                    </tableau-viz>
                </div>
                '''.format(url=url)
                break
        if html:
            return html
        return None


    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot).then(update_dashboard,chatbot,dashboard)
    
    clear.click(None, None, chatbot, queue=False)

    script = '''
    function test(){
        let script = document.createElement('script');
        script.innerHTML = "var viz = new tableau.Viz(containerDiv, document.getElementById('tableauViz').getAttribute('src'), {hideTabs: true});";
        document.head.appendChild(script);  
        }
    '''

    script2 = '''
    function test(){
        let script = document.createElement('script');
        script.type = 'module';
        script.src = 'https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js';
        document.head.appendChild(script);   
        }
    '''

    demo.load(_js = script)
    demo.load(_js = script2)
    
demo.queue()
#demo.launch()
demo.launch(share=True)

# COMMAND ----------


