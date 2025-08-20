from django.shortcuts import render, redirect

from .forms import RoomForm
from .models import Room

# Create your views here.


def index(request):
    return render(request, 'index.html', {"rooms": Room.objects.filter(active=True, hide_room=False)})


def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.owner = request.user
            room.save()
            return redirect('room_detail', room_id=room.id)
    else:
        form = RoomForm()
        return render(request, 'room_create.html', {"form": form})

def room_detail(request, room_id):
    room = Room.objects.get(id=room_id)
    return render(request, 'room_detail.html', {"room": room})

def room_spectate(request, room_id):
    pass

def room_play(request, room_id):
    pass

def ws_echo_test(request):
    return render(request, 'ws_echo_test.html')