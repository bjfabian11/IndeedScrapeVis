from flask import Flask, render_template, request, redirect
import requests
from bs4 import BeautifulSoup
from csv import writer
from bokeh.plotting import figure, output_file, show, save
import pandas
import time
import fileinput
import csv
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scraphit', methods = ['POST'])
def scraphit():
    searchUrl = request.form['searchUrl']
    kword1 = request.form['kword1']
    kword2 = request.form['kword2']
    kword3 = request.form['kword3']
    kword4 = request.form['kword4']
    kword5 = request.form['kword5']
    kword6 = request.form['kword6']
    
    response = requests.get(searchUrl)
    soup = BeautifulSoup(response.text, 'html.parser')

    with open('scrape.csv', 'w', encoding="utf-8") as csv_file:
        csv_writer = writer(csv_file)
        headers = ['Title', 'Company', 'Date',
                    'Location', 'Salary', 'Summary', 'Link']
        csv_writer.writerow(headers)

        def scrape():
            # find all Indeed job posts
            posts = soup.find_all(class_='jobsearch-SerpJobCard')
            # loop through posts
            for post in posts:
                # find job titles
                title = post.find(class_='title').get_text().replace('\n', '')
                # find company name
                if post.find(class_='company'):
                    company = post.find(class_='company').get_text().replace('\n', '')
                else:
                    company = 'no company'
                # find date posted
                date = post.find(class_='date').get_text()
                # find location
                if post.find(class_='location'):
                    location = post.find(class_='location').get_text()
                else:
                    location = 'no location'
                # find salary, if there is salary then search for it, else say "no data"
                if post.find(class_='salarySnippet'):
                    salary = post.find(class_='salarySnippet').get_text().replace('\n', '')
                else:
                    salary = 'no salary'
                # find summary
                if post.find(class_='summary'):
                    summary = post.find(class_='summary').get_text().replace('\n', '')
                else:
                    summary = 'no summary'
                # find link then add prefix to fullLink
                if post.find(class_='title').a['href']:
                    link = post.find(class_='title').a['href']
                    fullLink = 'https://www.indeed.com' + link
                else:
                    link = 'no link'             
                csv_writer.writerow([title, company, date, location, salary, summary, fullLink])

        #paginate through all pages from search results
        #--------------------
        #FAILED PAGINATION(inconsisten with actual amount of pages) Failed attempt to paginate through pages based off counting job results and dividing for a interation amount
        # #find number of pages from numnber jobs from search divided by 10
        # num_jobs = soup.find(id='searchCountPages').get_text()
        # job_num = num_jobs.split()
        # int_num = job_num[3].replace(',', '')
        # print(int_num, 'jobs')
        # pagination = int(int(int_num) / 10)
        # #iterate through pages calculated above and change url's &start= value
        # for i in range(pagination):
        #     start_num = str(i*10)
        #     nextUrl = searchUrl + '&start=' + str(start_num)
        #     print('scraping: ' + nextUrl)
        #     response = requests.get(nextUrl)
        #     time.sleep(1)
        #     soup = BeautifulSoup(response.text, 'html.parser')
        #--------------------
        #WORKING PAGINATION
        #find all class= np, which is the previous and next pagination buttons
        pag_next = soup.find_all(class_='np')
        #if there is no previous or next buttons there is only one page to scrape
        if len(pag_next) == 0:
            print('only one page')
            scrape()
            print('scraping: ' + searchUrl)
        #first page will contain only a next button(index 0)
        elif len(pag_next) == 1:
            print('first page')
            #scrape first page
            scrape()
            print('scraping: ' + searchUrl)
            response = requests.get('https://www.indeed.com' + pag_next[0].parent.parent['href'] + '&' + pag_next[0].parent.parent['data-pp'])
            time.sleep(.5)
            print('second page')
            #scrape second page
            scrape()
            print('scraping: https://www.indeed.com' + pag_next[0].parent.parent['href'] + '&' + pag_next[0].parent.parent['data-pp'])
            soup = BeautifulSoup(response.text, 'html.parser')
            pag_next = soup.find_all(class_='np')
        else:
            print('not equal to one')
        #all pages besides first and last will contain both previous and next button(index 1)
        while len(pag_next) > 1:
            print('middle page')
            nextUrl = 'https://www.indeed.com' + pag_next[1].parent.parent['href'] + '&' + pag_next[1].parent.parent['data-pp']
            response = requests.get(nextUrl)
            time.sleep(.5)
            #scrape the rest of the pages
            scrape()
            print('scraping: '+ nextUrl)
            soup = BeautifulSoup(response.text, 'html.parser')
            pag_next = soup.find_all(class_='np')
        else:
            print('no more pages')
            pass
    print('scrape.csv Created!')

    #Get rid of duplicates 
    # from CSV and add only unique Title, Company, Location combo to new array and into new CSV
    with open('scrape.csv', 'r', newline='') as inputfile:
        with open('scrape2.csv', 'w', encoding="utf-8", newline='') as outputfile:
            duplicatereader = csv.DictReader(inputfile, delimiter=',')
            uniquewrite = csv.DictWriter(outputfile, fieldnames=['Title', 'Company', 'Date', 'Location', 'Salary', 'Summary', 'Link'], delimiter=',')
            uniquewrite.writeheader()
            keysread = []
            for row in duplicatereader:
                #add header titles to be made into a unique pair to remove when they a duplicates
                key = (row['Title'], row['Company'], row['Location'])
                if key not in keysread:
                    keysread.append(key)
                    uniquewrite.writerow(row)
    print('removed duplicates')
    
    #open csv and count each post where users keyword was in the title or summary and write the totals in a new csv
    df = pandas.read_csv('scrape2.csv')
    count1 = len(df.loc[(df['Title'].str.contains(kword1, flags=re.I)) | (df['Summary'].str.contains(kword1, flags=re.I))])
    count2 = len(df.loc[(df['Title'].str.contains(kword2, flags=re.I)) | (df['Summary'].str.contains(kword2, flags=re.I))])
    count3 = len(df.loc[(df['Title'].str.contains(kword3, flags=re.I)) | (df['Summary'].str.contains(kword3, flags=re.I))])
    count4 = len(df.loc[(df['Title'].str.contains(kword4, flags=re.I)) | (df['Summary'].str.contains(kword4, flags=re.I))])
    count5 = len(df.loc[(df['Title'].str.contains(kword5, flags=re.I)) | (df['Summary'].str.contains(kword5, flags=re.I))])
    count6 = len(df.loc[(df['Title'].str.contains(kword6, flags=re.I)) | (df['Summary'].str.contains(kword6, flags=re.I))])
    #create csv and write totals
    with open('count.csv', 'w', encoding="utf-8") as csv_file:
        csv_writer = writer(csv_file)
        headers = ['Keyword', 'Count']
        csv_writer.writerow(headers)
        csv_writer.writerow([kword1, count1])
        csv_writer.writerow([kword2, count2])
        csv_writer.writerow([kword3, count3])
        csv_writer.writerow([kword4, count4])
        csv_writer.writerow([kword5, count5])
        csv_writer.writerow([kword6, count6])

    #create data frame of counted results from csv and visualize it in a graph using bokeh
    df_count = pandas.read_csv('count.csv')
    keyword = df_count['Keyword']
    count = df_count['Count']
    output_file('templates/scraphit.html')

    # Add plot
    p = figure(
        y_range=keyword,
        plot_width=800,
        plot_height=600,
        title="Scraph of " + searchUrl,
        x_axis_label='Count',
        # tools=''
    )

    # Render glyph
    p.hbar(
        y=keyword,
        right=count,
        left=0,
        height=0.4,
        color='blue',
        fill_alpha=0.5
    )

    # Save results
    save(p)
    print(searchUrl)
    print(df_count)
    return render_template('scraphit.html')
    
if __name__ == '__main__':
    app.debug = True
    app.run()