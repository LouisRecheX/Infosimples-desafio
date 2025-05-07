from bs4 import BeautifulSoup 
import requests 
import re
# Bibliotecas nativas do Python 
import json 
 
# URL do site 
url = 'https://infosimples.com/vagas/desafio/commercia/product.html' 
 
# Objeto contendo a resposta final 
resposta_final = {} 
 
# Faz o request 
response = requests.get(url) 
 
# Parse do responses 
parsed_html = BeautifulSoup(response.content, 'html.parser')


# buscando todas as div que tem class card
cards = parsed_html.select('div.card')


#definido como array vazio
produtos = []


# Aqui você adiciona os outros campos..

for card in cards:

    price = card.select_one('div.prod-pnow') 
    oldPrice = card.select_one('div.prod-pold') 
    productName = card.select_one('div.prod-nome')
    available = card.select_one('div.card.not-avaliable i')  
    
    
    if productName:
        productName = productName.get_text(strip=True)

    if price:
        price = float(price.get_text(strip=True).replace('R$', '').replace(',', '.'))

    if oldPrice:
        oldPrice = float(oldPrice.get_text(strip=True).replace('R$', '').replace(',', '.'))

    if available:
        available = available.get_text(strip=True)  
    else:
        available = "Disponível"  

    produto = { 
        "name": productName,
        'current_price ': price,
        'old_price ': oldPrice,
        'available': available,  
    }

    produtos.append(produto)



breadcrumbs_nav = parsed_html.select_one('nav.current-category')
categories = []

if breadcrumbs_nav:
    links = breadcrumbs_nav.select('a')
    for link in links:
        texto_categoria = link.get_text(strip=True)
        categories.append(texto_categoria)



description_tag = parsed_html.find('p', style=lambda s: s and 'text-align: justify' in s)

description = description_tag.get_text(strip=True) if description_tag else ""


title = parsed_html.select_one('h2#product_title').get_text() 
brand = parsed_html.select_one('div.brand').get_text() 
average_score_tag = parsed_html.select_one('#comments h4')

average_score = None
if average_score_tag:
    average_score_text = average_score_tag.get_text(strip=True)
    # Regex ajustada para capturar o número corretamente
    match = re.search(r'Average score:\s*([\d.]+)\s*\/\s*5', average_score_text)
    if match:
        average_score = float(match.group(1))


product_properties = {}


# Product properties
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

# Additional properties
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

    'brand' : brand,

    "categories": categories,

    "description": description,

    'skus': produtos,

    "properties": properties,

    "reviews": reviews_data,

    "reviews_average_score": average_score,

    "url": url,
    
}


# Salvando o JSON em um arquivo
with open('produto.json', 'w', encoding='utf-8') as json_file: 
    json.dump(resposta_final, json_file, indent=4, ensure_ascii=False)

# Mensagem no console informando que o Json foi criado
print("JSON gerado com sucesso.")