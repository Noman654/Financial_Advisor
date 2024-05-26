import requests
from bs4 import BeautifulSoup
import json
import re  # For regular expression matching


def get_stocks_code(text: str):


    url = "https://www.google.com/finance/_/GoogleFinanceUi/data/batchexecute?source-path=%2Ffinance%2F&bl=boq_finance-ui_20240519.00_p0&hl=en-GB"

    payload = {'f.req': [f'[[["mKsvE","[\\"{text}\\",null,1,1]",null,"generic"]]]']}

    headers = {
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'origin': 'https://www.google.com',
        'priority': 'u=1, i',
        'referer': 'https://www.google.com/',
        # Add your actual Google Finance cookie here (from browser inspection)
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # Extract JSON Data
    # Find the string that starts with a square bracket, which usually is after a comment
    json_str = re.search(r'\[.*\]', response.text, re.DOTALL).group(0)

    # Decode JSON
    data = json.loads(json_str)

    # Get news items from nested response
    stock_list = json.loads(data[0][2])


    stock_details_list  = []
    for d in stock_list[0]:
        stock_details_list.append((d[3][2],d[3][-1]))

    return stock_details_list


def get_news(quote:str) -> list:

    #  fetching  page from financial 
    url = f"https://www.google.com/finance/quote/{quote}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    #  convert page into readable format 
    soup = BeautifulSoup(response.content, "html.parser")

    #  reading news from page 
    news_section = soup.findAll(class_="yY3Lee")
    
    #  extracting needed information 
    data = []
    for news in news_section:
        temp_d = {}
        temp_d['news_source'] = news.find(class_='sfyJob').text
        temp_d['news_time'] = news.find(class_='Adak').text 
        temp_d['news_url'] = news.a.get('href')
        temp_d['news_text'] = news.find(class_="Yfwt5").text
        data.append(temp_d)
    
    return data