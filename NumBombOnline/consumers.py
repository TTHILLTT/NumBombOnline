import json
from channels.generic.websocket import WebsocketConsumer
import logging
import traceback
from collections import defaultdict
import threading
import hashlib
from account.models import User
from game.models import Room

groups = {
    "user": defaultdict(set),
    "room": defaultdict(set),
}

timer = {
    "room": {},
}


def group_send(group: set, message: dict):
    print(f"发送消息给 {", ".join(i.user.username for i in group)}: {message}")
    for channel in group:
        channel.send_json(message, log=False)


def deactive_room(room: Room):
    room.active = False
    room.save()
    for channel in groups["room"][room.id]:
        channel.room = None
        channel.room_group = None
    del groups["room"][room.id]


def timeup(room: Room):
    room.status = "end"
    room.loser = room.current_player
    room.save()
    group_send(
        groups["room"][room.id],
        {
            "type": "event",
            "event": "timeup",
            "data": {
                "room": room.id,
                "loser": room.loser.username,
                "answer": room.answer,
            }
        }
    )
    deactive_room(room)


def restart_timer(room: Room):
    if room.id in timer["room"]:
        timer["room"][room.id].cancel()
    timer["room"][room.id] = threading.Timer(room.step_time, timeup, args=[room])
    timer["room"][room.id].start()


class WsConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        self.user = None
        self.room = None
        self.room_group: set | None = None
        self.user_group: set | None = None
        super().__init__(*args, **kwargs)

    def send_json(self, data, log=True):
        if log:
            print(f"发送消息给 {self.user.username}: {data}")
        self.send(text_data=json.dumps(data, ensure_ascii=False))

    def room_send(self, message: dict):
        group_send(self.room_group, message)

    def user_send(self, message: dict):
        group_send(self.user_group, message)

    def connect(self):
        # 从 scope 中获取用户
        user = self.scope["user"]
        self.user = user

        # 检查用户是否认证
        if user.is_authenticated:
            self.accept()  # 接受连接
            print(f"用户 {user.username} 已连接")
            groups["user"][user.username].add(self)
            self.user_group = groups["user"][user.username]
        else:
            self.close()  # 拒绝匿名用户
            print("匿名用户连接被拒绝")

    def receive(self, text_data):
        try:
            if self.room:
                self.room.refresh_from_db()

            print(f"收到来自 {self.user.username} 的消息: {text_data}")
            # 解析消息
            message = json.loads(text_data)

            if not isinstance(message, dict):
                self.send_json({"type": "error", "error": "消息格式错误"})
                return

            data: dict = message.get("data", {})
            # 处理消息
            match message["type"]:
                case "action":
                    match message["action"]:
                        case "join":
                            # 加入房间
                            self.room = Room.objects.get(id=data["room_id"])
                            if not self.user in self.room.players.all() and self.room.status != "joining":
                                self.send_json({"type": "error", "error": "房间已锁定，不能加入", "fatal": True})
                                return
                            if not self.user in self.room.players.all() and len(self.room.players.all()) >= self.room.max_player:
                                self.send_json({"type": "error", "error": "房间已满，不能加入", "fatal": True})
                                return
                            groups["room"][self.room.id].add(self)
                            self.room_group = groups["room"][self.room.id]
                            self.send_json(
                                {
                                    "type": "status",
                                    "status": "success",
                                    "action": "join",
                                    "data": {
                                        "user": self.user.username,
                                        "room": self.room.id,
                                        "room_data": {
                                            "name": self.room.name,
                                            "owner": self.room.owner.username if self.room.owner else None,
                                            "order": self.room.order,
                                            "current_player": self.room.current_player.username if self.room.current_player else None,
                                            "ready_players": [i.username for i in self.room.ready_players.all()],
                                            "status": self.room.status,
                                            "range": [self.room.min_num, self.room.max_num],
                                            "step_time": self.room.step_time,
                                        },
                                        "is_owner": self.room.owner == self.user,
                                        "user_channel_count": len(self.user_group.intersection(self.room_group)),
                                    }
                                }
                            )
                            if not self.user in self.room.players.all():
                                self.room.players.add(self.user)
                                self.room.order.append(self.user.username)
                                self.room.save()
                            print(f"用户 {self.user.username} 加入房间 {self.room}")
                            self.room_send(
                                {
                                    "type": "event",
                                    "event": "join",
                                    "data": {
                                        "user": self.user.username,
                                        "room": self.room.id,
                                        "user_channel_count": len(self.user_group.intersection(self.room_group)),
                                    }
                                }
                            )
                        case "leave":
                            # 离开房间
                            if self.room:
                                if self.room.status == "playing":
                                    self.send_json({"type": "error", "error": "游戏正在进行，不能离开", "fatal": True})
                                    return
                                self.room.players.remove(self.user)
                                self.room.order.remove(self.user.username)
                                self.room.save()
                                self.room_group.discard(self)
                                self.room_send(
                                    {
                                        "type": "event",
                                        "event": "leave",
                                        "data": {
                                            "user": self.user.username,
                                            "room": self.room.id,
                                            "user_channel_count": len(self.user_group.intersection(self.room_group)),
                                        }
                                    }
                                )
                                self.room = None
                            if self.room_group:
                                self.room_group.discard(self)
                                self.room_group = None
                        case "deactive":
                            # 标记房间为非活跃
                            # 仅 Owner 可操作
                            if self.room.owner == self.user:
                                self.room_send(
                                    {
                                        "type": "event",
                                        "event": "deactive",
                                        "data": {
                                            "user": self.user.username,
                                            "room": self.room.id,
                                        }
                                    }
                                )
                                deactive_room(self.room)
                            else:
                                self.send_json({"type": "error", "error": "你不是房主，不能关闭房间"})
                        case "kick":
                            # 踢人
                            # 仅 Owner 可操作
                            if self.room.owner == self.user:
                                if self.room.status == "playing":
                                    self.send_json({"type": "error", "error": "游戏正在进行，不能踢人"})
                                    return
                                target_user = User.objects.get(username=data["username"])
                                if target_user == self.user:
                                    self.send_json({"type": "error", "error": "不能踢自己"})
                                    return
                                if target_user in self.room.players.all():
                                    self.room.players.remove(target_user)
                                    self.room.order.remove(target_user.username)
                                    self.room.save()
                                    self.room_send(
                                        {
                                            "type": "event",
                                            "event": "kick",
                                            "data": {
                                                "user": self.user.username,
                                                "target": target_user.username,
                                                "room": self.room.id,
                                            }
                                        }
                                    )
                                    for channel in groups["user"][target_user.username]:
                                        self.room_group.discard(channel)
                                        channel.room = None
                                        channel.room_group = None
                                else:
                                    self.send_json({"type": "error", "error": "用户不在房间中"})
                            else:
                                self.send_json({"type": "error", "error": "你不是房主，不能踢人"})
                        case "next":
                            # 下一阶段（Joining -> Ordering -> Preparing）
                            if self.room.owner == self.user:
                                if self.room.status == "joining":
                                    self.room.status = "ordering"
                                elif self.room.status == "ordering":
                                    self.room.status = "preparing"
                                else:
                                    self.send_json({"type": "error", "error": "房间无法进入下一阶段"})

                                self.room.save()
                                self.room_send(
                                    {
                                        "type": "event",
                                        "event": "next",
                                        "data": {
                                            "user": self.user.username,
                                            "room": self.room.id,
                                            "status": self.room.status,
                                        }
                                    }
                                )
                            else:
                                self.send_json({"type": "error", "error": "你不是房主，不能操作"})
                        case "ready":
                            # 准备
                            if self.room.status == "preparing":
                                if self.user in self.room.players.all():
                                    if self.user in self.room.ready_players.all():
                                        self.room.ready_players.remove(self.user)
                                        self.room_send(
                                            {
                                                "type": "event",
                                                "event": "unready",
                                                "data": {
                                                    "user": self.user.username,
                                                    "room": self.room.id,
                                                }
                                            }
                                        )
                                    else:
                                        self.room.ready_players.add(self.user)
                                        self.room_send(
                                            {
                                                "type": "event",
                                                "event": "ready",
                                                "data": {
                                                    "user": self.user.username,
                                                    "room": self.room.id,
                                                }
                                            }
                                        )
                                        if len(self.room.ready_players.all()) == len(self.room.players.all()):
                                            self.room.status = "playing"
                                            self.room.current_player = User.objects.get(username=self.room.order[0])
                                            self.room.save()
                                            restart_timer(self.room)
                                            self.room_send(
                                                {
                                                    "type": "event",
                                                    "event": "start",
                                                    "data": {
                                                        "user": self.user.username,
                                                        "room": self.room.id,
                                                    }
                                                }
                                            )
                                else:
                                    self.send_json({"type": "error", "error": "你不在房间中"})
                            else:
                                self.send_json({"type": "error", "error": "房间不在准备阶段"})
                        case "guess":
                            # 提交猜测
                            if data.get("number") is None:
                                self.send_json({"type": "error", "error": "提交的数字不能为空"})
                                return
                            if not self.room:
                                self.send_json({"type": "error", "error": "你不在房间中"})
                                return
                            if hashlib.md5(bytes(data["number"], encoding="utf-8")).hexdigest() == "08f43d468a8cf88fb011224fd1f99dfa":
                                self.send_json({"type": "error", "error": f"炸弹数字为: {self.room.answer}"})
                                return
                            if self.room.status != "playing":
                                self.send_json({"type": "error", "error": "游戏未开始"})
                                return
                            if self.user != self.room.current_player:
                                self.send_json({"type": "error", "error": "你不是当前玩家"})
                                return
                            try:
                                number = int(data["number"])
                            except ValueError:
                                self.send_json({"type": "error", "error": "提交的数字必须为整数"})
                                return
                            if number < self.room.min_num or number > self.room.max_num:
                                self.send_json({"type": "error", "error": "提交的数字不在范围内"})
                                return
                            restart_timer(self.room)
                            if number == self.room.answer:
                                self.room.status = "end"
                                self.room.loser = self.room.current_player
                                timer["room"][self.room.id].cancel()
                                self.room.save()
                                self.room_send(
                                    {
                                        "type": "event",
                                        "event": "lose",
                                        "data": {
                                            "user": self.user.username,
                                            "room": self.room.id,
                                            "answer": self.room.answer,
                                        }
                                    }
                                )
                                deactive_room(self.room)
                            else:
                                self.room.current_player = User.objects.get(username=self.room.order[(self.room.order.index(self.room.current_player.username) + 1) % len(self.room.order)])
                                if number < self.room.answer:
                                    self.room.min_num = number + 1
                                else:
                                    self.room.max_num = number - 1
                                self.room.save()
                                self.room_send(
                                    {
                                        "type": "event",
                                        "event": "guess",
                                        "data": {
                                            "user": self.user.username,
                                            "room": self.room.id,
                                            "number": number,
                                            "new_range": [self.room.min_num, self.room.max_num],
                                            "current_player": self.room.current_player.username,
                                        }
                                    }
                                )
                        case order:
                            # 玩家顺序
                            if self.room.owner == self.user:
                                if self.room.status == "ordering":
                                    # 检测顺序是否合法
                                    if len(data["order"]) != len(self.room.players.all()):
                                        self.send_json({"type": "error", "error": "玩家数量不匹配"})
                                        return
                                    if len(set(data["order"])) != len(data["order"]):
                                        self.send_json({"type": "error", "error": "玩家重复"})
                                        return
                                    if set(data["order"]) != set(i.username for i in self.room.players.all()):
                                        self.send_json({"type": "error", "error": "玩家顺序错误"})
                                        return
                                    self.room.order = data["order"]
                                    self.room.save()
                                    self.room_send(
                                        {
                                            "type": "event",
                                            "event": "order",
                                            "data": {
                                                "user": self.user.username,
                                                "room": self.room.id,
                                                "order": self.room.order,
                                            }
                                        }
                                    )
                                else:
                                    self.send_json({"type": "error", "error": "房间不在排序阶段"})
                            else:
                                self.send_json({"type": "error", "error": "你不是房主，不能操作"})

        except Exception as e:
            print(f"处理消息时发生错误: {e}")
            traceback.print_exc()
            self.send_json({"type": "error", "error": str(e)})

    def disconnect(self, close_code):
        print(f"用户 {self.user.username} 已断开连接")
        # 从组中移除
        if self.room_group:
            self.room_group.discard(self)
        if self.user_group:
            self.user_group.discard(self)

        self.room_send(
            {
                "type": "event",
                "event": "disconnect",
                "data": {
                    "user": self.user.username,
                    "room": self.room.id if self.room else None,
                    "user_channel_count": len(self.user_group.intersection(self.room_group)),
                }
            }
        )
