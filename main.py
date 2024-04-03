import sqlite3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def scrape_and_store_data():
    """
    Scrape data from a website and store it in a SQLite database.
    """
    url = 'https://www.worldometers.info/population/countries-in-the-eu-by-population/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    table = soup.find('table', {'id': 'example2'})
    rows = table.find_all('tr')
    for row in rows[1:]:
        cells = row.find_all('td')
        country = cells[1].text.strip()
        population = int(cells[2].text.strip().replace(',', ''))
        data.append((country, population))

    # Store the scraped data in the database
    conn = sqlite3.connect('eu_population.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS population')  # Drop the table if it already exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS population (
                        id INTEGER PRIMARY KEY,
                        country TEXT,
                        population INTEGER
                    )''')
    cursor.executemany('INSERT INTO population (country, population) VALUES (?, ?)', data)

    conn.commit()
    conn.close()

    print("Data has been successfully scraped and stored.")

def visualize_data():
    """
    Visualize the data from the database
    """
    conn = sqlite3.connect('eu_population.db')
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

def export_data():
    """
    Export data from a SQLite database to a CSV file.
    """
    conn = sqlite3.connect('eu_population.db')

    # Read data from database into dataframe
    df = pd.read_sql_query('SELECT * FROM population', conn)

    # Export dataframe to CSV file
    df.to_csv('eu_population.csv', index=False)
    print("Data has been successfully exported to 'eu_population.csv'.")
    conn.close()

if __name__ == "__main__":
    scrape_and_store_data()
    visualize_data()
    export_data()
