from bs4 import BeautifulSoup 
import requests 
import re
import json 

url = 'https://infosimples.com/vagas/desafio/commercia/product.html' 

resposta_final = {} 

response = requests.get(url) 

parsed_html = BeautifulSoup(response.content, 'html.parser')

cards = parsed_html.select('div.card')

produtos = []

for card in cards:
    price_tag = card.select_one('div.prod-pnow') 
    old_price_tag = card.select_one('div.prod-pold') 
    name_tag = card.select_one('div.prod-nome')
    not_available_icon = card.select_one('div.card.not-avaliable i')  

    product_name = name_tag.get_text(strip=True) if name_tag else None
    price = float(price_tag.get_text(strip=True).replace('R$', '').replace(',', '.')) if price_tag else None
    old_price = float(old_price_tag.get_text(strip=True).replace('R$', '').replace(',', '.')) if old_price_tag else None

    available = False if not_available_icon else True

    produto = { 
        "name": product_name,
        "current_price": price,
        "old_price": old_price,
        "available": available
    }

    produtos.append(produto)

breadcrumbs_nav = parsed_html.select_one('nav.current-category')
categories = []

if breadcrumbs_nav:
    links = breadcrumbs_nav.select('a')
    for link in links:
        texto_categoria = link.get_text(strip=True)
        categories.append(texto_categoria)

description_tags = parsed_html.find_all('p', style=lambda s: s and 'text-align:justify' in s.replace(" ", "").lower())
description = " ".join(tag.get_text(strip=True) for tag in description_tags)




title = parsed_html.select_one('h2#product_title').get_text() 
brand = parsed_html.select_one('div.brand').get_text() 
average_score_tag = parsed_html.select_one('#comments h4')

average_score = None
if average_score_tag:
    average_score_text = average_score_tag.get_text(strip=True)
    match = re.search(r'Average score:\s*([\d.]+)\s*\/\s*5', average_score_text)
    if match:
        average_score = float(match.group(1))

product_properties = {}
product_properties_section = None
for h4 in parsed_html.find_all("h4"):
    if "Product properties" in h4.get_text(strip=True):
        product_properties_section = h4.find_next_sibling("table")
        break

if product_properties_section:
    rows = product_properties_section.select('tr')
    for row in rows:
        property_name = row.select_one('td b')
        property_value = row.select_one('td:nth-child(2)')
        if property_name and property_value:
            product_properties[property_name.get_text(strip=True)] = property_value.get_text(strip=True)

additional_properties = {}
additional_properties_section = None
for h4 in parsed_html.find_all("h4"):
    if "Additional properties" in h4.get_text(strip=True):
        additional_properties_section = h4.find_next_sibling("table")
        break

if additional_properties_section:
    rows = additional_properties_section.select('tr')
    for row in rows:
        property_name = row.select_one('td b')
        property_value = row.select_one('td:nth-child(2)')
        if property_name and property_value:
            additional_properties[property_name.get_text(strip=True)] = property_value.get_text(strip=True)

properties = []

if product_properties_section:
    rows = product_properties_section.select('tr')
    for row in rows:
        property_name = row.select_one('td b')
        property_value = row.select_one('td:nth-child(2)')
        if property_name and property_value:
            properties.append({
                "label": property_name.get_text(strip=True),
                "value": property_value.get_text(strip=True)
            })

if additional_properties_section:
    rows = additional_properties_section.select('tr')
    for row in rows:
        property_name = row.select_one('td b')
        property_value = row.select_one('td:nth-child(2)')
        if property_name and property_value:
            properties.append({
                "label": property_name.get_text(strip=True),
                "value": property_value.get_text(strip=True)
            })

reviews_data = []
reviews_section = parsed_html.select_one('div#comments') 

if reviews_section:
    reviews = reviews_section.select('div.analisebox')  
    for review in reviews:
        user_name = review.select_one('span.analiseusername')  
        review_date = review.select_one('span.analisedate')  
        review_rating = review.select_one('span.analisestars')  
        review_text = review.select_one('p')  
        
        if user_name:
            user_name = user_name.get_text(strip=True)
        else:
            user_name = "Desconhecido"

        if review_date:
            review_date = review_date.get_text(strip=True)
        else:
            review_date = "Data não disponível"

        if review_rating:
            review_rating = review_rating.get_text(strip=True).replace("☆", "" )
            review_rating = len(review_rating)
        else:
            review_rating = 0

        if review_text:
            review_text = review_text.get_text(strip=True)
        else:
            review_text = "Sem comentário"
        
        reviews_data.append({
            "name": user_name,
            "date": review_date,
            "score": review_rating,
            "text": review_text
        })

resposta_final = { 
    "title" : title,
    "brand" : brand,
    "categories": categories,
    "description": description,
    "skus": produtos,
    "properties": properties,
    "reviews": reviews_data,
    "reviews_average_score": average_score,
    "url": url,
}

with open('produto.json', 'w', encoding='utf-8') as json_file: 
    json.dump(resposta_final, json_file, indent=4, ensure_ascii=False)

print("JSON gerado com sucesso.")

