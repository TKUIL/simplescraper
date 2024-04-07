import sqlite3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_population_data():
    """
    Scrape population data from the provided website.
    """
    try:
        url = 'https://www.worldometers.info/population/countries-in-the-eu-by-population/'
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for invalid HTTP responses
        soup = BeautifulSoup(response.text, 'html.parser')

        population_data = []
        table = soup.find('table', {'id': 'example2'})
        if table:
            rows = table.find_all('tr')
            for row in rows[1:]:
                cells = row.find_all('td')
                country = cells[1].text.strip()
                population = int(cells[2].text.strip().replace(',', ''))
                population_data.append((country, population))
        else:
            print("Population table not found on the webpage.")

        return population_data
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the HTTP request:", e)
        return []

def scrape_university_data():
    """
    Scrape university data from the API.
    """
    try:
        api_url = 'http://universities.hipolabs.com/search?name='
        university_response = requests.get(api_url)
        university_response.raise_for_status()  # Raise an error for invalid HTTP responses
        university_data = university_response.json()

        # Extract relevant data
        university_data_to_store = [(university['country'], university['name'], university['alpha_two_code'], ', '.join(university['web_pages'])) for university in university_data]

        return university_data_to_store
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the API request:", e)
        return []


# no work
'''
def scrape_top_universities(year, country='All countries', max_items=100, mode='basic'):
    """
    Scrape top university data from the provided website using Selenium with Firefox WebDriver.
    """
    try:
        options = Options()
        options.headless = True  # Run Firefox in headless mode

        driver = webdriver.Firefox(options=options)

        url = f'https://www.topuniversities.com/university-rankings/world-university-rankings/{year}'
        driver.get(url)

        # Wait for the page to fully load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '._qs-ranking-data-row')))

        universities = []

        # Set "Results per page" select field to show all universities
        dropdown = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sort_by_dropdown .dropdown')))
        dropdown.click()

        # Scroll the page
        driver.execute_script('window.scrollBy({ top: document.body.scrollHeight / 2 })')

        # Wait for the dropdown options to load
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.sort_by_dropdown div[data-value="100"]')))

        # Click on the option to show 100 items per page
        option_100 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.sort_by_dropdown div[data-value="100"]')))
        option_100.click()

        # Set country filter
        if country != 'All countries':
            print(f"Setting desired country {country}...")
            country_select = driver.find_element(By.CSS_SELECTOR, '.country-select-realdiv #country-select')
            country_select.send_keys(country.lower())

        # Get the total number of results
        number_of_results = int(driver.find_element(By.CSS_SELECTOR, '#_totalcountresults').text.strip())
        print(f"Found {number_of_results} results in total.")

        # COUNTER OF ITEMS TO SAVE
        items_counter = 0

        # Get data from the page based on the mode
        if mode == 'visit_detail':
            detail_urls = [link.get_attribute('href') for link in driver.find_elements(By.CSS_SELECTOR, '.uni-link')]
            for url in detail_urls:
                if items_counter >= max_items:
                    break
                universities.append({'detail_page': url})
                items_counter += 1
        else:
            # Basic mode
            rows = driver.find_elements(By.CSS_SELECTOR, '.ind')
            for row in rows:
                if items_counter >= max_items:
                    break
                title = row.find_element(By.CSS_SELECTOR, '.uni-link').text.strip()
                rank = row.find_element(By.CSS_SELECTOR, '._univ-rank').text.strip()
                overall_score = row.find_element(By.CSS_SELECTOR, '.overall-score-span').text.strip()
                country = row.find_element(By.CSS_SELECTOR, '.location').text.strip()
                detail_page = row.find_element(By.CSS_SELECTOR, '.uni-link').get_attribute('href')
                universities.append({'title': title, 'QS_world_university_ranking': rank, 'overall_score': overall_score, 'country': country, 'detail_page': detail_page})
                items_counter += 1

        driver.quit()  # Close the browser

        return universities
    except Exception as e:
        print("An error occurred while scraping top universities:", e)
        return []
'''

def store_data_in_database(population_data, university_data):
    """
    Store population data and university data in separate tables within the same SQLite database.
    """
    conn = sqlite3.connect('universities.db')
    cursor = conn.cursor()

    try:
        # Create population table
        cursor.execute('''CREATE TABLE IF NOT EXISTS population (
                            id INTEGER PRIMARY KEY,
                            country TEXT,
                            population INTEGER
                        )''')
        cursor.executemany('INSERT INTO population (country, population) VALUES (?, ?)', population_data)

        # Create universities table
        cursor.execute('''CREATE TABLE IF NOT EXISTS universities (
                            id INTEGER PRIMARY KEY,
                            country TEXT,
                            name TEXT,
                            alpha_two_code TEXT,
                            web_pages TEXT
                        )''')
        cursor.executemany('INSERT INTO universities (country, name, alpha_two_code, web_pages) VALUES (?, ?, ?, ?)', university_data)

        conn.commit()
        print("Data has been successfully scraped and stored.")
    except sqlite3.Error as e:
        print("An error occurred while storing data in the database:", e)
    finally:
        conn.close()

def visualize_population_data():
    """
    Visualize the population data from the database.
    """
    try:
        conn = sqlite3.connect('universities.db')
        df = pd.read_sql_query('SELECT * FROM population', conn)
        conn.close()

        plt.figure(figsize=(10, 6))
        bars = plt.barh(df['country'], df['population'], color='skyblue')
        plt.xlabel('Population')
        plt.title('Population of EU Countries from worldometers.info')
        plt.gca().invert_yaxis()

        # Add numbers to the bars
        for bar in bars:
            plt.text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width()):,}',
                     va='center', ha='left', fontsize=8, color='black')

        plt.show()
    except sqlite3.Error as e:
        print("An error occurred while visualizing population data:", e)

def export_data_to_csv():
    """
    Export data from SQLite database to CSV files.
    """
    try:
        conn = sqlite3.connect('universities.db')

        # Read data from population table into dataframe
        df_population = pd.read_sql_query('SELECT * FROM population', conn)

        # Read data from universities table into dataframe
        df_universities = pd.read_sql_query('SELECT * FROM universities', conn)

        # Read data from top universities table into dataframe
        df_top_universities = pd.read_sql_query('SELECT * FROM top_universities', conn)

        conn.close()

        # Export dataframes to CSV files
        df_population.to_csv('eu_population.csv', index=False)
        df_universities.to_csv('universities.csv', index=False)
        df_top_universities.to_csv('top_universities.csv', index=False)
        
        print("Data has been successfully exported to 'eu_population.csv', 'universities.csv', and 'top_universities.csv'.")
    except sqlite3.Error as e:
        print("An error occurred while exporting data to CSV files:", e)

def scrape_and_store_data():
    """
    Scrape data from websites and store it in a SQLite database.
    """
    try:
        # Scrape population data
        population_data = scrape_population_data()

        # Scrape university data
        university_data = scrape_university_data()

        # Store the scraped data in the database
        store_data_in_database(population_data, university_data)
    except Exception as e:
        print("An unexpected error occurred:", e)


if __name__ == "__main__":
    scrape_and_store_data()
    visualize_population_data()
    export_data_to_csv()
