# -*- coding: utf-8 -*-
"""
Created on Tue May 30 20:19:08 2017

@author: Ryan
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import re
import pandas

weather_url = 'https://www.wunderground.com/history/airport/KARB/2017/4/1/DailyHistory.html?req_city=Ann+Arbor&req_state=MI&req_statename=Michigan&reqdb.zip=48103&reqdb.magic=1&reqdb.wmo=99999'
river_url = 'https://waterdata.usgs.gov/nwis/dv?cb_00010=on&cb_00060=on&cb_00095=on&cb_00300=on&cb_00400=on&format=rdb&site_no=04174518&referred_module=sw&period=&begin_date=2017-05-04&end_date=2017-05-29'
#later change this so you can input the number of different river no.  Find position of no=, delete the number after, and then you can add a new number there whenever.  Maybe wrap everything in a class that parses all that out
#also change this when you make it dynamic to incorporate todays date in the end of the website url.  Consider changing start date as well


#I will probably want to make this two classes, one for the weather and one for the river urls
class WeatherScrape():
    def __init__(self, url):
        self.url = url
        self.soup = self.make_soup()
    
    def new_date(self, date):
        self.url = re.sub('\d{4}/\d{1,2}/\d{1,2}',date, self.url)
        self.soup = self.make_soup()
        
    def make_soup(self):
        html = urlopen(self.url).read()
        return bs(html, "lxml")
    
    def get_precipitation(self):
        try:
            prec = float(self.soup.findAll('tr')[14].findAll('td')[1].find('span', 'wx-value').get_text())
        except:
            #for whatever reason some of the web pages are formated stupidlylike
            prec = float(self.soup.findAll('tr')[13].findAll('td')[1].find('span', 'wx-value').get_text())
        return prec
    
    def get_temperature(self):
        return float(self.soup.findAll('tr')[2].findAll('td')[1].find('span', 'wx-value').get_text())

class RiverScrape():
    def __init__(self, url):
        self.url = url

    def get_river_data(self, url):
        #this function takes data from a really simple website layout, which is why I only
        #need to decode it rather than run it through beautifulsoup
        return urlopen(self.url).read().decode('utf-8')
    
    def river_data_list(self):
        data = self.get_river_data(self.url)
        return [j.split('\t') for j in [i for i in data.split('\n')[:-1] if i[0] != '#']][2:]
     
  
if __name__ == '__main__':
    huronRiverData = RiverScrape(river_url)
    
    d_list = huronRiverData.river_data_list()
    flow_data = []
    for i, j in enumerate(d_list):
        flow_data.append([j[2].replace('-', '/'), float(j[3])])
    
    weather_object = WeatherScrape(weather_url)
    
    
    for i, item in enumerate(flow_data):
        weather_object.new_date(item[0])
        #flow_data[i] = [weather_object.get_temperature(), weather_object.get_precipitation()] + flow_data[i]
        flow_data[i] = [weather_object.get_precipitation()] + flow_data[i]
    
    training_data = []
    for i in range(len(flow_data)-3):
        #previous 3 days rain/flow are inputs into the NN
        training_data += [[flow_data[i-3][0], flow_data[i-2][0], flow_data[i-1][0], flow_data[i-3][2], flow_data[i-2][2], flow_data[i-1][2], flow_data[i][2]]]