import requests
import csv
import re
from bs4 import BeautifulSoup

def get_wikipedia_data(search_terms, limit=10):
    base_url = 'https://id.wikipedia.org/w/api.php'
    all_results = []
    
    for term in search_terms:
        search_params = {
            'action': 'query',
            'format': 'json',
            'list': 'search',
            'srsearch': f'intitle:"{term}" (smartphone OR ponsel)',
            'srlimit': limit
        }
        try:
            response = requests.get(base_url, params=search_params)
            response.raise_for_status()
            search_results = response.json().get('query', {}).get('search', [])
            
            for item in search_results:
                detail_params = {
                    'action': 'query',
                    'format': 'json',
                    'prop': 'extracts|info|images',
                    'exintro': True,
                    'explaintext': True,
                    'inprop': 'url',
                    'pageids': item['pageid']
                }
                detail_response = requests.get(base_url, params=detail_params)
                detail_response.raise_for_status()
                page = detail_response.json().get('query', {}).get('pages', {}).get(str(item['pageid']), {})
                
                extract = page.get('extract', '')
                title = item['title']
                
                # Filter out non-smartphone entries
                if not is_smartphone(extract, title, term):
                    continue
                
                model = title.replace(term, '').strip()
                release_year = extract_release_year(extract)
                image_url = get_image_src(page.get('fullurl', ''))
                
                all_results.append({
                    'brand': term,
                    'model': model,
                    'release_year': release_year,
                    'image_url': image_url,
                    'snippet': item['snippet'].replace('<span class="searchmatch">', '').replace('</span>', '').replace(',', ';'),
                    'extract': extract[:500] + '...' if len(extract) > 500 else extract,
                    'fullurl': page.get('fullurl', '')
                })
            
            print(f"Fetched {len(all_results)} smartphone results for {term}")
        
        except requests.RequestException as e:
            print(f'Error fetching data for {term} from Wikipedia: {e}')
    
    return all_results

def is_smartphone(extract, title, brand):
    smartphone_keywords = ['smartphone', 'ponsel pintar', 'ponsel cerdas', 'telepon genggam']
    if not any(brand.lower() in title.lower() and keyword in title.lower() for keyword in ['galaxy', 'iphone', 'redmi', 'mi ', 'poco', 'tab', 'ipad', 'pad', 'zenfone']):
        return False 
    return any(keyword in extract.lower() or keyword in title.lower() for keyword in smartphone_keywords)

def extract_release_year(text):
    year_match = re.search(r'\b(20\d{2})\b', text)
    return year_match.group(1) if year_match else 'Unknown'

def get_image_src(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        infobox = soup.find('table', class_='infobox')
        if infobox:
            img_tag = infobox.find('img')
            if img_tag and 'src' in img_tag.attrs:
                return 'https:' + img_tag['src'] if img_tag['src'].startswith('//') else img_tag['src']
    except requests.RequestException as e:
        print(f'Error fetching image src: {e}')
    
    return 'Image src not found'

def convert_to_csv(data, filename):
    if not data:
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def main():
    try:
        brands = ["Samsung", "Apple", "Xiaomi", "Oppo", "Vivo", "Huawei", "Realme", "OnePlus", "Sony", "LG", "Nokia", "Asus", "Lenovo"]
        
        results = get_wikipedia_data(brands, limit=50)  # Increased limit to potentially get more valid results
        
        if results:
            convert_to_csv(results, 'smartphone_data.csv')
            print('Data berhasil disimpan ke smartphone_data.csv')
            print(f'Jumlah smartphone yang ditemukan: {len(results)}')
        else:
            print('Tidak ditemukan informasi smartphone.')
    except Exception as e:
        print(f'Terjadi kesalahan: {e}')

if __name__ == '__main__':
    main()