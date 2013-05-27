#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import os.path
import sys
import pycurl
import cStringIO
import json
import urllib2
import httplib
import urllib
import urlparse
import BaseHTTPServer
import webbrowser
from datetime import datetime
import sqlite3
import filtro
 
APP_ID = '124412807757420'
APP_SECRET = '05869394e6909522e30bc623a7b48eb5'
ENDPOINT = 'graph.facebook.com'
REDIRECT_URI = 'http://localhost:8000/'
ACCESS_TOKEN = None
 
def get_url(path, args=None):
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

 
def get(path, args=None):
    return urllib2.urlopen(get_url(path, args=args)).read()
 
class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
 
    def do_GET(self):
        global ACCESS_TOKEN
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
 
        code = urlparse.parse_qs(urlparse.urlparse(self.path).query).get('code')
        code = code[0] if code else None
        if code is None:
            self.wfile.write("Sorry, authentication failed.")
            sys.exit(1)
        response = get('/oauth/access_token?', {'client_id':APP_ID,
                                               'redirect_uri':REDIRECT_URI,
                                               'client_secret':APP_SECRET,
                                               'code':code})
        ACCESS_TOKEN = urlparse.parse_qs(response)['access_token'][0]
        open(LOCAL_FILE,'w').write(ACCESS_TOKEN)
        self.wfile.write("You have successfully logged in to facebook. "
                         "You can close this window now.")

def download_image(url,id):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    fichero = open('/tmp/' + str(id) + '.jpg',"wb")
    fichero.write(response.read())
    fichero.close()


def store_friends():
    friends_dict={}
    for item in json.loads(get('/me/friends?fields=birthday,picture.height(500),name&',None))['data']:
        if 'birthday' in item:
            friend_data=[]
            friend_data.append(item['id'])
            friend_data.append(item['name'])
            friend_data.append(item['birthday'])
            friend_data.append(item['picture']['data']['url'])    
            friends_dict[item['id']] = friend_data
    #-----------------------------------
    #Parte de prueba si no hay amigos de cumpleaños. Felipe "esta de cumpleaños" de este modo.
    friend_data_aux=[]
    friend_data_aux.append('1403781713')
    friend_data_aux.append('Felipe Alvarado')
    friend_data_aux.append('06/03/1991')
    friend_data_aux.append('https://fbcdn-profile-a.akamaihd.net/hprofile-ak-frc1/295791_4771668855330_445453724_n.jpg')
    friends_dict['1403781713']=friend_data_aux
    #-----------------------------------Fin parte de prueba
    return friends_dict


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

    return (day == today)
    

def upload_congratulation(file_path,message,friend_id):
    global ACCESS_TOKEN
    url = 'https://graph.facebook.com/' + str(friend_id) + '/photos'
    response = cStringIO.StringIO()
    c = pycurl.Curl()
    values = [
        ('source' , (c.FORM_FILE,  file_path)),
        ('access_token' , ACCESS_TOKEN),
        ('message' , message)]
    c.setopt(c.POST, 1)
    c.setopt(c.URL,url)
    c.setopt(c.HTTPPOST,  values)
    #c.setopt(c.VERBOSE, 1) #descomentar en caso de Necesitarse Debug. Si el access_token esta caducado, aqui se producirá un fallo.
    c.setopt(c.WRITEFUNCTION, response.write)
    c.perform()
    c.close()

def store_friends_birthday(dictionary):
    dictionary_congratulation={}
    #for item in dictionary:
        #if ( its_birthday(dictionary[item][2])== True):
            #dictionary_congratulation[item] = dictionary[item]

    #----------------------------
    #Parte de prueba si no hay amigos de cumpleaños. Felipe "esta de cumpleaños" de este modo.
    dictionary_congratulation['1403781713'] = dictionary['1403781713']
    #----------------FIN PARTE DE PRUEBA
    return dictionary_congratulation



if __name__ == '__main__':
    connection = sqlite3.connect('/home/raul/Escritorio/django/www/appcumple/appcumple.db')
    cursor = connection.cursor()
    message="Felicidades! Difrutalos mucho"
    fichero_log=open("/home/raul/Escritorio/django/www/appcumple/log_automatico.log","w")
    cursor.execute('SELECT * FROM avicumple_users')
    for user in cursor:
        fichero_log.write("-------------------------------------------------------------\n")
        fichero_log.write("User "+str(user[1])+" with Facebook_ID: "+ str(user[3])+"\n")
        ACCESS_TOKEN=user[4].encode("UTF-8")
        try:
            array=json.loads(get('/me?',None))
        except:
            print "Usuario invalido"
            fichero_log.write("User "+str(user[1])+" with Facebook_ID: "+ str(user[3])+" has an invalid Facebook authorization\n")
            continue
        dictionary = store_friends()
        birthday_friends=store_friends_birthday(dictionary)
        for friend in birthday_friends:
            try:
                download_image(birthday_friends[friend][3],birthday_friends[friend][0])
                file_path_origin="/tmp/"+str(birthday_friends[friend][0])+".jpg"
                file_path_destiny="/tmp/"+str(birthday_friends[friend][0])+"2.jpg"
                filtro.filtro(file_path_origin,file_path_destiny)
                upload_congratulation(file_path_destiny,message,birthday_friends[friend][0])
                fichero_log.write("ALL RUN CORRECTLY\n")
            except:
                fichero_log.write("User "+str(user[1])+" with Facebook_ID: "+ str(user[3])+" was NOT ABLE to congratulate the user "+str(birthday_friends[friend][2])+":"+str(birthday_friends[friend][0])+"\n")
                continue

    fichero_log.close()
                


