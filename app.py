# from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from csv import writer
from bokeh.plotting import figure, output_file, show
import pandas
import time

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('index.html')

# if __name__ == '__main__':
#     app.debug = True
#     app.run()

# Scrape Indeed URL and create CSV file
searchUrl = 'https://www.indeed.com/jobs?q=python+developer&l=Wadsworth%2C+OH&radius=50'
response = requests.get(searchUrl)
soup = BeautifulSoup(response.text, 'html.parser')

with open('scrape.csv', 'w') as csv_file:
    csv_writer = writer(csv_file)
    headers = ['Title', 'Company', 'Date',
                'Location', 'Salary', 'Summary', 'Link']
    csv_writer.writerow(headers)

    #find number of pages from numnber jobs from search divided by 10
    num_jobs = soup.find(id='searchCountPages').get_text()
    job_num = num_jobs.split()
    int_num = job_num[3].replace(',', '')
    print(int_num, 'jobs')
    pagination = int(int(int_num) / 10)
    #iterate through pages calculated above and change url's &start= value
    for i in range(pagination):
        start_num = str(i*10)
        nextUrl = searchUrl + '&start=' + str(start_num)
        print('scraping: ' + nextUrl)
        response = requests.get(nextUrl)
        time.sleep(1)
        soup = BeautifulSoup(response.text, 'html.parser')
        # find all Indeed job posts
        posts = soup.find_all(class_='jobsearch-SerpJobCard')
        # loop through posts
        for post in posts:
            # find job titles
            title = post.find(class_='title').get_text().replace('\n', '')
            # find company name
            company = post.find(class_='company').get_text().replace('\n', '')
            # find date posted
            date = post.find(class_='date').get_text()
            # find location
            location = post.find(class_='location').get_text()
            # find salary, if there is salary then search for it, else say "no data"
            if post.find(class_='salarySnippet'):
                salary = post.find(
                    class_='salarySnippet').get_text().replace('\n', '')
            else:
                salary = 'no data'
            # find summary
            summary = post.find(class_='summary').get_text().replace('\n', '')
            # find link then add prefix to fullLink
            link = post.find(class_='title').a['href']
            fullLink = 'https://www.indeed.com' + link
            csv_writer.writerow([title, company, date, location, salary, summary, fullLink])
print('scrape.csv Created!')