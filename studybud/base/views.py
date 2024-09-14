from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm

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
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
 
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home') #Sends user back to home page
        else:
            messages.error(request, 'Username OR password does not exist.')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST': #Pass in user data
        form = UserCreationForm(request.POST)
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

    topics = Topic.objects.all()
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

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False) #Gives us instance of the room
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form' : form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) 

    if request.user != room.host: #User most be the host of the room in order to edit it 
        return HttpResponse('You are not allowed here!!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room) #Updates the current room instance, and doesn't make a new post instead.
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
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

