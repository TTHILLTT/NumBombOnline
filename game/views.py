from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import unquote
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
            return redirect('room_play', room_id=room.id)
    else:
        form = RoomForm()
        return render(request, 'room_create.html', {"form": form})


def room_detail(request, room_id):
    room = Room.objects.get(id=room_id)
    return render(request, 'room_detail.html', {"room": room})


def room_spectate(request, room_id):
    pass


def room_play(request, room_id):
    # 生成URL后解码
    raw_url = reverse('profile_username', args=['${user}'])
    decoded_url = unquote(raw_url)  # 这一步会把%7B转换回{，%7D转换回}
    return render(request, 'room_play.html', {"room": Room.objects.get(id=room_id), 'profile_url': decoded_url})


def ws_echo_test(request):
    return render(request, 'ws_echo_test.html')
