# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from avicumple.models import Users,Friends
from django.core.exceptions import ObjectDoesNotExist
from avicumple.modulo_facebook import *
import re
import unicodedata

def login(request):
	error_message=""
	friend_list=Friends.objects.all().order_by('name')

	friend_list.delete()

	if request.session.has_key('access_token'):
		del request.session['access_token']
	if request.POST.has_key('user') and request.POST.has_key('pass'):
		try:
			user=request.POST['user']
			password=request.POST['pass']
			u=Users.objects.get(usuario=user,password=password)
			request.session['access_token']=u.acces_token
			array=json.loads(get('/me?',None,request.session['access_token']))
			context={'error_message':error_message}
			return render(request,'avicumple/list.html',context)
		except ObjectDoesNotExist:
			error_message="User or Pass not exists"
		except :
			del request.session['access_token']
			u.delete()
			error_message="Your Facebook authorization has expired, and consequently your user has been DISABLED. Please register again and authorize the application."
			u.delete

	context={'error_message':error_message}
	return render(request,'avicumple/login.html',context)

def register(request):
	error_message=""
	ACCESS_TOKEN=""
	authurl="YES"
	show_authorize_message="YES"
	if request.GET.has_key('code'):
		code = request.GET['code']
		if code is None:
			error_message = "Facebook authorization failed"
		else:		
			response = get('/oauth/access_token?', {'client_id':APP_ID,
                                               'redirect_uri':REDIRECT_URI+"avicumple/register/",
                                               'client_secret':APP_SECRET,
                                               'code':code})
			ACCESS_TOKEN = urlparse.parse_qs(response)['access_token'][0]
			request.session['access_token']=ACCESS_TOKEN
			show_authorize_message=""
	else:
		authurl=get_url('/oauth/authorize?',
                                {'client_id':APP_ID,
                                 'redirect_uri':REDIRECT_URI+"avicumple/register/",
                                 'scope':'read_stream,friends_birthday,publish_stream'})


	if request.POST.has_key('user') and request.POST.has_key('pass') :	
		user = request.POST['user']
		password = request.POST['pass']
		if not user or not password or not request.session.has_key('access_token'):
			error_message="You don't Authorize Facebook or you miss to put your user or password"
		else:
			try:
				u=Users.objects.get(usuario=user)
				error_message="The user name is already in use. Please put other user name"
			except ObjectDoesNotExist:
				u=Users(usuario=user,password=password,id_fb=0,acces_token=request.session['access_token'])	
				u.save()
				del request.session['access_token']
				context={'error_message':error_message,'authurl':authurl}
				return render(request,'avicumple/login.html',context)

	else:
		error_message='Please, enter your data'

	context={'error_message':error_message,'authurl':authurl,'show_authorize_message':show_authorize_message}
	return render(request,'avicumple/register.html',context)

def list(request):
	error_message=""
	birthday_list_message=""
	message_ok=""
	friend_list=Friends.objects.all().order_by('name')
	reload_all_friends=""
	if request.POST.has_key('all_friends'):
		friend_list.delete()
		try:
			array=json.loads(get('/me/friends?fields=birthday,picture.height(500),name&',None,request.session['access_token']))['data']
			for item in array:
				if 'birthday' in item:
					Friends.objects.create(id_fb=item['id'],name=item['name'],date=item['birthday'],photo=item['picture']['data']['url'])
				else: 
					Friends.objects.create(id_fb=item['id'],name=item['name'],date='none',photo=item['picture']['data']['url'])
			friend_list=Friends.objects.all().order_by('name')
		except:
			error_message="Oh, so sorry, an unexpected error has occurred. Please, LOGIN AGAIN."
			context={'error_message':error_message}
			return render(request,'avicumple/login.html',context)

	if request.POST.has_key('birthday_friends'):
		searched_friends=[]
		reload_all_friends="yes"
		for f in friend_list:
			reload_all_friends=""
			if f.date != "none":
				birthday_list_message="You don't have friends on birthday"
				if its_birthday(f.date):
					birthday_list_message="There are friends birthday"
					searched_friends.append(f.id_fb)			
		friend_list=Friends.objects.filter(id_fb__in=searched_friends).order_by('name')
	
	if request.POST.has_key('congratulate_all'):
		for f in friend_list:
			if f.date != "none":
				if its_birthday(f.date):
					try:			
						download_image(f.photo,f.id_fb)
						apply_filter(f.id_fb)
						file_path="/tmp"
						message="Felicidades disfrutalos mucho"
						ACCESS_TOKEN=request.session['access_token']
						upload_congratulation(message,f.id_fb,ACCESS_TOKEN.encode("UTF-8"))
						message_ok="You have congratulated your friends"
					except:
						error_message="Oh, so sorry, an unexpected error has occurred. Please, LOGIN AGAIN."
						context={'error_message':error_message}
						return render(request,'avicumple/login.html',context)

	if request.POST.has_key('logout'):
		friend_list.delete()
		if request.session.has_key('access_token'):
			del request.session['access_token']
		context={}
		return render(request,'avicumple/login.html',context)
	if request.POST.has_key('search_button'):
		search_in=request.POST['search']
		searched_friends=[]
		search=".*"+search_in+".*"
		for f in friend_list:
			search_clean = unicodedata.normalize("NFKD", search).encode("ascii", "ignore")
			name = unicodedata.normalize("NFKD", f.name).encode("ascii", "ignore")
			try:
				if (re.match(search_clean,name,re.IGNORECASE)):
					searched_friends.append(f.id_fb)
			except:
				error_message="Invalid regular expresion."
		friend_list=Friends.objects.filter(id_fb__in=searched_friends).order_by('name')

	context={'friend_list':friend_list,'error_message':error_message,'birthday_list_message':birthday_list_message,
'message_ok':message_ok,'reload_all_friends':reload_all_friends}
	return render(request,'avicumple/list.html',context)

def detail(request,id_fb):
	try:
		f=Friends.objects.get(id_fb=id_fb)
	except ObjectDoesNotExist:
			error_message="The user ID you are looking for does not exist."
			friend_list=Friends.objects.all().order_by('name')
			context={'error_message':error_message,'friend_list':friend_list}
			return render(request,'avicumple/list.html',context)

	message_ok=""
	congratulate_button=""
	error_message=""
	if f.date != "none":
		if its_birthday(f.date):
			congratulate_button="show"
	if request.POST.has_key('congratulate'):
		try:
			download_image(f.photo,id_fb)	
			apply_filter(id_fb)
			message="Felicidades disfrutalos mucho"
			ACCESS_TOKEN=request.session['access_token']
			upload_congratulation(message,id_fb,ACCESS_TOKEN.encode("UTF-8"))
			message_ok="You have congratulated your friend"
		except:
			error_message="Oh, so sorry, an unexpected error has occurred. Please, LOGIN AGAIN."
			context={'error_message':error_message}
			return render(request,'avicumple/login.html',context)

	context={'f':f,'message_ok':message_ok,'congratulate_button':congratulate_button,'error_message':error_message}
	return render(request,'avicumple/detail.html',context)



		




