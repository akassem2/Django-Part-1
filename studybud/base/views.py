from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

#rooms = [
#    {'id': 1, 'name':"Let's learn python!"},
#    {'id': 2, 'name':"Design with me"},
#    {'id': 3, 'name':"Frontend Developers"},
#]

def loginPage(request):

    page = 'login'

    if request.user.is_authenticated: #Will return the user to the home page if they try to login in when already logged in. 
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')
 
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home') #Sends user back to home page
        else:
            messages.error(request, 'Email OR password does not exist.')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST': #Pass in user data
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) #Gets the user name
            user.username = user.username.lower() #Makes it lower case
            user.save()
            login(request, user) #Will save their data properly and log them in, then send them to the home page. 
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registeration.')
    
    return render(request, 'base/login_register.html', {'form': form})


def home(request): 
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter( #Use Q for dynamic search bar
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
        )

    topics = Topic.objects.all()[0:5] #Limits the topics displayed in the home page to 5
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))#Could modify this to where you only see people you follow instead


    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all().order_by('-created') #Give us the set of messages that are related to this room, also ordered by most recent message.
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user) #Adds the user to the participant list
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() #Get all the children of an object my doing modelname_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, "topics": topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form' : form, 'topic': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) 
    topics = Topic.objects.all()
    if request.user != room.host: #User most be the host of the room in order to edit it 
        return HttpResponse('You are not allowed here!!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host: #User most be the host of the room in order to delete it 
        return HttpResponse('You are not allowed here!!!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user: #User most be owner of the message in order to delete it 
        return HttpResponse('You are not allowed here!!!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id) #Lets the user edit their profile, saves it, and sends them back to their profile.

    return render(request, 'base/update-user.html', {'form': form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})

def activityPage(request):
    room_messages = Message.objects.all() 
    return render(request, 'base/activity.html', {'room_messages': room_messages})