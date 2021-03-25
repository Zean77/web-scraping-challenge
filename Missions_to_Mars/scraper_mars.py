# Dependencies
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from splinter import Browser
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pandas as pd
import pprint

def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()

    # webpage to be scraped
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    html = browser.html
    soup = bs(html, 'html.parser')

    # retrieve the latest news title
    news_title = soup.find('div',class_='content_title').text.strip()
    print(news_title)
    # retrieve the latest news paragraph
    news_p = soup.find('div', class_='article_teaser_body').text.strip()
    print(news_p)

    #JPL Mars Space Images - Featured Image
    jpl_url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(jpl_url)
    # HTML object
    html=browser.html
    # Parse HTML
    soup=bs(html,"html.parser")
    # Retrieve image url
    image=soup.find('div', class_="sm:object-cover object-cover")
    image_url = image.find('img')['src']
    featured_image_url=image_url
    print(featured_image_url)

    #Mars Facts
    # scrape the html and retrieve all tables
    fact_url = 'https://space-facts.com/mars/'
    tables=pd.read_html(fact_url)
    print(tables)

    # select the first table that contains relevant information
    mars_fact=tables[0]
    # convert to dataframe
    mars_fact=mars_fact.rename(columns={0:"Description",1:"Value"})
    mars_fact.set_index("Description",inplace=True)

    # convert to html format
    html_table=mars_fact.to_html()
    print(html_table)

    #Mars Hemispheres¶
    # website to be scraped using beautifulSoup
    hemi_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hemi_url)
    html=browser.html
    soup=bs(html,'html.parser')

    # Extract hemispheres item elements to load to the image page
    mars_hem = soup.find('div', class_='collapsible results')
    images = mars_hem.find_all('div', class_='item')

    # create a dictionary to hold scraped values
    hemisphere_image_urls=[]
    # loop through 4 hemispheres
    for img in images:
        result = img.find('div', class_='description')
        # find 4 mars hemisphere titles
        title = result.h3.text
        # loop through each of these 4 urls and scrape images
        img_url = img.find('a')['href']
        browser.visit("https://astrogeology.usgs.gov"+ img_url)
        html=browser.html
        soup=bs(html,'html.parser')
        downloads = soup.find('div', class_='downloads')
        img_src = downloads.find("a")["href"]
        # print output
        if (title and img_src):
            print('-'*70)
            print(title)
            print(img_src)
        # attach value to the dictionary
        hemisphere_image_urls.append({
            'title': title,
            'img_url': img_src
        })
    
    # Create a dictionary to hold all information scraped from above websites
    mars_info = {
        'title': news_title,
        'news_content': news_p,
        'featured_image_url': featured_image_url,
        'mars_facts': html_table,
        'hemisphere_images': hemisphere_image_urls
    }

    # close the browser
    browser.quit()
    return mars_info