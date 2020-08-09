# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from avicumple.models import Users,Friends
from django.core.exceptions import ObjectDoesNotExist
from avicumple.modulo_facebook import *
import re
import unicodedata

from datetime import date

def login(request):
	error_message=""

	if request.session.has_key('access_token'):
		del request.session['access_token']
	if request.POST.has_key('user') and request.POST.has_key('pass'):
		# Mocked ACCESS_TOKEN
		request.session['access_token'] = "random_string"

		context={'error_message':error_message}
		return render(request,'avicumple/list.html',context)

	context = {'error_message': error_message}
	return render(request, 'avicumple/login.html', context)

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
	birthday_image=""
	if request.POST.has_key('all_friends'):
		friend_list.delete()
		try:
			Friends.objects.create(id_fb=123456, name='Julio Iglesias', date=date.today().strftime("%m/%d/%Y"),
									   photo='https://estaticos.elperiodico.com/resources/jpg/3/8/aplazan-juicio-paternidad-contra-julio-iglesias-1547641520183.jpg')
			Friends.objects.create(id_fb=123457, name='Marcelo', date='10/10/1992',
								   photo='https://www.ambientum.com/wp-content/uploads/2018/06/cabra-pupilas-rectangulares-BOLETIN.jpg')

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

					download_image(f.photo,f.id_fb)
					apply_filter(f.id_fb)
					file_path="/tmp"
					birthday_image=str(f.id_fb)+"2.jpg"
					message="Felicidades disfrutalos mucho"
					# ACCESS_TOKEN=request.session['access_token']
					# upload_congratulation(message,id_fb,ACCESS_TOKEN.encode("UTF-8"))
					message_ok="You have congratulated your friends"


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
'message_ok':message_ok,'reload_all_friends':reload_all_friends,'birthday_image':birthday_image}
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
	birthday_image=""
	if f.date != "none":
		if its_birthday(f.date):
			congratulate_button="show"
	if request.POST.has_key('congratulate'):
		try:
			download_image(f.photo,id_fb)	
			apply_filter(id_fb)
			birthday_image = str(f.id_fb) + "2.jpg"
			message="Felicidades disfrutalos mucho"
			ACCESS_TOKEN=request.session['access_token']
			#upload_congratulation(message,id_fb,ACCESS_TOKEN.encode("UTF-8"))
			message_ok="You have congratulated your friend"
		except:
			error_message="Oh, so sorry, an unexpected error has occurred. Please, LOGIN AGAIN."
			context={'error_message':error_message}
			return render(request,'avicumple/login.html',context)

	context={'f':f,'message_ok':message_ok,'congratulate_button':congratulate_button,'error_message':error_message,
			 'birthday_image':birthday_image}
	return render(request,'avicumple/detail.html',context)



		




