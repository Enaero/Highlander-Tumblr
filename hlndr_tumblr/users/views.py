#Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context, loader, RequestContext
from django.utils import timezone
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

# from users.models import User
from users.forms import RegisterForm, LoginForm, ImageForm
from users.models import UserProfile

def profile(request, username):
    user = get_object_or_404(User,username=username)
    userprofile = get_object_or_404(UserProfile,user=user)
    return render_to_response('users/profile.html', {'user':user, 'userprofile':userprofile}, context_instance=RequestContext(request))

# login page
def log_in(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return HttpResponseRedirect('/dashboard/')
				else:
					return render_to_response('users/login.html',
											  {'form':form,
											   'invalid':"Account disabled"},
											  context_instace=RequestContext(request))
			else:
				return render_to_response('users/login.html',
										  {'form':form,
										   'invalid':"Invalid username or password"},
										  context_instance=RequestContext(request))

	template = loader.get_template('users/login.html')
	context = RequestContext(request)
	return HttpResponse(template.render(context))

@login_required(login_url='/login/')
def log_out(request):
	logout(request)
	return HttpResponseRedirect('/')

@login_required(login_url='/login/')
def editProfilePhoto(request):
	if request.method == 'POST':
		forms = ImageForm(request.POST, request.FILES)
		if forms.is_valid():
			file = request.FILES['image']
			#we may want to add an id field here to prevent user from accidently overriding
			filePath = "%s/ProfilePhote/%s/" % (request.user.username, file.name)
			s3_thread(file, filePath)
			request.user.userprofile.avatar = amazon_url + filePath
			request.user.userprofile.save()
			userName = request.user.username
			return HttpResponseRedirect("%s/profile" % userName)
	else:
		form = ImageForm()
	return render_to_response("users/editprofile.html",
							  {'users':request.user,'form':form},
							  context_instance=RequestContext(request))

# registration page
def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			
			# Validate fields
			if form.cleaned_data['password1'] == form.cleaned_data['password2']:
				password = form.cleaned_data['password1']
			else:
				return render_to_response('users/register.html',
										  {'form':form,
										   'invalid':"Passwords mismatched"},
										   context_instance=RequestContext(request))
			
			# Django User Data
			username = form.cleaned_data['username']
			email = form.cleaned_data['email']
			
			# User Profile Data
			birthday = form.cleaned_data['birthday']
			nickname = form.cleaned_data['nickname']
			gender = form.cleaned_data['gender']
			interests = form.cleaned_data['interests']
			
			# Save User to database
			newuser = User(username=username,email=email)
			newuser.set_password(password)
			newuser.save()
			
			# save user profile to database
			user = User.objects.get(username=username)
			newUserProfile = UserProfile.objects.create(user=user,
														birthday=birthday,
														nickname=nickname,
														gender=gender,
														interests=interests)
			return HttpResponseRedirect('/login/')
		else:
			return render_to_response('users/register.html',
									  {'form':form,
									   'invalid':"Some required fields have not been filled"},
									  context_instance=RequestContext(request))
	else:
		form = RegisterForm()

	return render_to_response('users/register.html',
							  context_instance=RequestContext(request))	
