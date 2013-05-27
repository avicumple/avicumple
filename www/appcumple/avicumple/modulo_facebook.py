#!/usr/bin/python
import os.path
import json
import urllib2
import urllib
import pycurl
import cStringIO
import urlparse
from datetime import datetime
from avicumple.filtro import filtro

APP_ID = '124412807757420'
APP_SECRET = '05869394e6909522e30bc623a7b48eb5'
ENDPOINT = 'graph.facebook.com'
REDIRECT_URI = 'http://localhost:8000/'
 
def get_url(path, args=None,ACCESS_TOKEN=None):
    args = args or {}
    if ACCESS_TOKEN:
        args['access_token'] = ACCESS_TOKEN
    if 'access_token' in args or 'client_secret' in args:
        endpoint = "https://"+ENDPOINT
    else:
        endpoint = "http://"+ENDPOINT
    salida = endpoint+path+urllib.urlencode(args)
    #print 'Debug :' + salida
    return salida

 
def get(path, args=None, ACCESS_TOKEN=None):
    return urllib2.urlopen(get_url(path, args=args, ACCESS_TOKEN=ACCESS_TOKEN)).read()

def its_birthday(birthday_date):
    today = datetime.today() #fecha actual
    if len(birthday_date) < 7 :
        today = today.replace(year = 1900, hour = 0, minute = 0, second = 0, microsecond = 0)
        day = datetime.strptime(birthday_date, "%m/%d")
        day = day.replace(year = 1900, hour = 0, minute = 0, second = 0, microsecond = 0)
    else :
        today = today.replace(year = 1900, hour = 0, minute = 0, second = 0, microsecond = 0)
        day = datetime.strptime(birthday_date, "%m/%d/%Y")
        day = day.replace(year = 1900, hour = 0, minute = 0, second = 0, microsecond = 0)
        #print today
    return (day == today)

def download_image(url,id_fb):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    fichero = open('/tmp/' + str(id_fb) + '.jpg',"wb")
    fichero.write(response.read())
    fichero.close()

def apply_filter(id_fb):
    url="/tmp/"+str(id_fb)+".jpg"
    url2="/tmp/"+str(id_fb)+"2.jpg"
    filtro(url,url2)

def upload_congratulation(message,id_fb,ACCESS_TOKEN):
    url = 'https://graph.facebook.com/' + str(id_fb) + '/photos'
    response = cStringIO.StringIO()
    c = pycurl.Curl()
    file_path="/tmp/"+str(id_fb)+"2.jpg"
    array=json.loads(get('/me?',None,ACCESS_TOKEN))
    values = [
        ('source' , (c.FORM_FILE,  file_path)),
        ('access_token' , ACCESS_TOKEN),
        ('message' , message)]
    c.setopt(c.POST, 1)
    c.setopt(c.URL,url)
    c.setopt(c.HTTPPOST,  values)
    #c.setopt(c.VERBOSE, 1) 
    c.setopt(c.WRITEFUNCTION, response.write)
    c.perform()
    c.close()
