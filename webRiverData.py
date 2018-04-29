# -*- coding: utf-8 -*-
"""
Created on Tue May 30 20:19:08 2017

@author: Ryan
"""
from pprint import pprint
from keras.models import Sequential
from keras.layers import Dense

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import re

weather_url = 'https://www.wunderground.com/history/airport/KARB/2017/4/1/DailyHistory.html?req_city=Ann+Arbor&req_state=MI&req_statename=Michigan&reqdb.zip=48103&reqdb.magic=1&reqdb.wmo=99999'
river_url = 'https://waterdata.usgs.gov/nwis/dv?cb_00010=on&cb_00060=on&cb_00095=on&cb_00300=on&cb_00400=on&format=rdb&site_no=04174518&referred_module=sw&period=&begin_date=2015-03-29&end_date=2018-03-29'
#later change this so you can input the number of different river no.  Find position of no=, delete the number after, and then you can add a new number there whenever.  Maybe wrap everything in a class that parses all that out
#also change this when you make it dynamic to incorporate todays date in the end of the website url.  Consider changing start date as well

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
        prec_locations = [14,13,11]

        for i, item in enumerate(prec_locations):
            prec = self.soup.findAll('tr')[item].findAll('td')[1].find('span', 'wx-value')
            if prec:
                return float(prec.get_text())
        return None
    
    def get_temperature(self):
        try:
            temp = float(self.soup.findAll('tr')[2].findAll('td')[1].find('span', 'wx-value').get_text())
        except:
            #sometimes, there is no value for temperature.  In that case, we average the min and max
            temp1 = float(self.soup.findAll('tr')[3].findAll('td')[2].find('span', 'wx-value').get_text())
            temp2 = float(self.soup.findAll('tr')[4].findAll('td')[2].find('span', 'wx-value').get_text())
            temp = (temp1+temp2)/2
        return temp
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
        flow_data[i] = [weather_object.get_temperature(), weather_object.get_precipitation()] + flow_data[i]  #temp might work as an indicator of season
    
##currently, flow_data is [rainfall, date, flow]

    training_x_data = []
    training_y_data = []

    
    for j in range(len(flow_data)-3):
        #previous 3 days rain/flow are inputs into the NN
        i = j + 3
        training_x_data += [[flow_data[i-3][0], flow_data[i-2][0], flow_data[i-1][0], flow_data[i-3][1], flow_data[i-2][1], flow_data[i-1][1], flow_data[i-3][3], flow_data[i-2][3], flow_data[i-1][3], flow_data[i][3]]]
        #training_y_data += [flow_data[i][3]]

    f = open('data.txt', 'a')
    f.write('Temp 3 \t Temp 2 \t Temp 1\t Prec 3\t Prec 2\t Prec 1\t Flow 3\t Flow 2\t Flow 1\t Target Flow\t \n')
    for i in training_x_data:
        for j in i:
            f.write('{}\t'.format(j))
        f.write('\n')
    f.close()
                  

'''    
    test_x_data = training_x_data[-10:]
    test_y_data = training_y_data[-10:]
    training_x_data = training_x_data[:-10]
    training_y_data = training_y_data[:-10]
    
    model = Sequential()
    model.add(Dense(12, input_dim=8, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
''' 

    
    
