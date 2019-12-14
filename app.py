# from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from csv import writer

# app = Flask(__name__)


# @app.route('/')
# def index():
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.debug = True
#     app.run()   

response = requests.get('https://www.indeed.com/jobs?q=Python+Developer&l=Wadsworth,+OH&radius=50/')

soup = BeautifulSoup(response.text, 'html.parser')

posts = soup.find_all(class_='jobsearch-SerpJobCard')

with open('scrape.csv', 'w') as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Title', 'salary', 'Link']
    csv_writer.writerow(headers)

    for post in posts:
        title = post.find(class_='title').get_text().replace('\n', '')
        if post.find(class_='salarySnippet'):
            salary = post.find(class_='salarySnippet').get_text().replace('\n', '') 
        else:
            salary = 'no data'
        link = post.find(class_='title').a['href']
        fullLink = 'https://www.indeed.com' + link
        csv_writer.writerow([title, salary, fullLink])