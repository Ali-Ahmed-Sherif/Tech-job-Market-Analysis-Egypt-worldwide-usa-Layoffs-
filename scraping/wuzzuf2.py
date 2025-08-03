# Imports
import requests
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import itertools
import pandas as pd

# The first page of the search result for with search input "python"
URL = 'https://wuzzuf.net/search/jobs/?a=hpb&q=software&start=0'

# Empty container lists
page = 0
companies = []
titles = []
locations = []
skills = []
contracts = []
links = []

# Loop through pages until page 144
while True:
    page_url = f'{URL[:-1]}{page}'
    
    result = requests.get(page_url)
    result_content = result.content
    soup = BeautifulSoup(result_content, 'lxml')

    # Total job count (parsed safely)
    ad_number = int(soup.find('strong').text.replace(',', ''))

    job_titles = soup.find_all("a", {'class': 'css-o171kl', 'rel': 'noreferrer'})
    location_names = soup.find_all('span', {'class': 'css-5wys0k'})
    contract_type = soup.find_all('div', {'class': 'css-1lh32fc'})
    job_skills = soup.find_all('div', {'class': 'css-y4udm8'})
    company_names = soup.find_all("a", {'class': 'css-17s97q8'})

    page_len = len(company_names)

    for item in range(page_len):
        companies.append(company_names[item].text)
        links.append(job_titles[item].attrs['href'])
        titles.append(job_titles[item].text)
        locations.append(location_names[item].text)
        skills.append(job_skills[item].text)
        contracts.append(contract_type[item].text)
    
    page += 1
    reached_ad = int(soup.find('li', class_='css-8neukt').text.split()[3])
    print(f'Page: {page}, ads: {reached_ad}')
    
    # ✅ Stop at page 144 exactly
    if reached_ad >= 2620:
        print('✅ Reached 2620 ads — stopping.')
        break

# Selenium to extract salary info
options = webdriver.FirefoxOptions()
options.headless = True
driver = webdriver.Firefox(options=options)


# Create and save DataFrame
df = pd.DataFrame(list(itertools.zip_longest(
    titles, companies, locations, contracts, skills, links, 
    fillvalue='not fetched')),
    columns=['Title', 'Company', 'Location', 'Contract', 'Skills', 'Link'])

df.to_csv('jobs_wuzzuf_data_jobs_softwarejobs.csv', index=False, encoding='utf-8')
print(f'✅ File created: {len(df)} jobs saved to jobs_wuzzuf_data_jobs.csv')
