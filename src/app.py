import sqlite3
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import seaborn as sns
import pandas as pd


resource_url = "https://ycharts.com/companies/TSLA/revenues"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class Scraping:
    def __init__(self, resource_url, headers):
        self.resource_url = resource_url
        self.html = None
        self.headers = headers

    def download(self):
        self.html = requests.get(self.resource_url, headers=self.headers)

    def display_html(self):
        pass
        #print(self.html.text)

    def parse_html(self):
        parsed_html = BeautifulSoup(self.html.text, "html.parser")
        return parsed_html

    def display_tables(self, parsed_html):
        tables = parsed_html.find_all("table")
        return tables

    def find_div(self, parsed_html):
        divs = parsed_html.find_all('div', class_='panel-content')
        for div in divs:
            thead = div.find('thead')
            return thead

    def store_table_df(self, parsed_html):
        df = pd.DataFrame(columns=["Date", "Revenue"])
        rows = []
        tbody = parsed_html.find('tbody').find_all('tr')
        for tr in tbody:
            td = tr.find_all('td')
            date = td[0].text.strip().replace(',', '')
            value = td[1].text.strip().replace('B', '')
            rows.append([date, value])
        df = pd.DataFrame(rows, columns=["Date", "Revenue"])
        return df
    
class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS historical (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, revenue REAL)")
        self.connection.commit()

    def insert_data(self, df):
        df.to_sql('historical', self.connection, if_exists='append', index=False)

    def read_data(self):
        self.cursor.execute("SELECT * FROM historical")
        data = self.cursor.fetchall()
        return data

    def close_connection(self):
        self.connection.close()

class Plotting:
    def __init__(self, connection):
        self.connection = connection

    def db_to_df(self):
        df = pd.read_sql("SELECT * FROM historical", self.connection)
        df['date'] = pd.to_datetime(df['date'], format='%B %d %Y')
        df['year'] = df['date'].dt.year #extracting the year
        df['month'] = df['date'].dt.month #extracting the month
        return df

    def line_plot(self, df):
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='date', y='revenue')
        plt.title('Historical Revenue')
        plt.xlabel('Date')
        plt.ylabel('Revenue')
        plt.savefig("line_plot.jpg",dpi=300)
        plt.show()

    def annual_revenue_plot(self,df):
        by_year = df.groupby('year')['revenue'].sum().reset_index()
        sns.barplot(data=by_year, x='year', y='revenue')
        plt.title('Annual  Benefit')
        plt.xlabel('Year')
        plt.ylabel('Revenue')
        plt.tight_layout()
        plt.savefig("barplot_year.jpg", dpi=300)
        plt.show()

    #in colab display different barplot 
    def monthly_revenue_plot(self,df):
        by_month = df.groupby('month')['revenue'].sum().reset_index() # grouping the data by month and i get the revenue for each month.
        sns.barplot(data=by_month,x='month', y='revenue')
        plt.title('Monthly  Benefit')
        plt.xlabel('Months')
        plt.ylabel('Revenue')
        plt.tight_layout()
        plt.savefig("barplot_month.jpg", dpi=300)
        plt.show()

scraping = Scraping(resource_url, headers)
scraping.download()
scraping.display_html()
parsed_html = scraping.parse_html()
tables = scraping.display_tables(parsed_html)
divs = scraping.find_div(parsed_html)

df = scraping.store_table_df(parsed_html)

db = Database('tesla.db')
db.connect()
db.create_table()
db.insert_data(df)

myplot = Plotting(db.connection)
database_df = myplot.db_to_df()
myplot.line_plot(database_df)
myplot.annual_revenue_plot(database_df)
myplot.monthly_revenue_plot(database_df)
db.close_connection()
