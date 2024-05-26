import stock_adviser as sa 
import scrap_news as sn 


import vertexai
from vertexai.preview.generative_models import GenerativeModel, ChatSession
import os
from google.oauth2 import service_account
from google.cloud import aiplatform





# 1. Agent which take user input as  a text 

# u get a text on n 
n = 'tata'

stockes_code = sn.get_stocks_code(n)

# 3. print the stock code so user can see and select 

# 4 once user choose retur it which stockes it choose 

# 5  what user selected  show to the user 