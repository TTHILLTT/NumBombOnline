from channels.generic.websocket import AsyncWebsocketConsumer


class WsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 从 scope 中获取用户
        user = self.scope["user"]

        # 检查用户是否认证
        if user.is_authenticated:
            await self.accept()  # 接受连接
            print(f"用户 {user.username} 已连接")
        else:
            await self.close()  # 拒绝匿名用户
            print("匿名用户连接被拒绝")

    async def receive(self, text_data):
        # 任何时候都可以通过 scope 获取用户
        current_user = self.scope["user"]
        print(f"收到来自 {current_user.username} 的消息: {text_data}")

    # ... 其他方法 (disconnect 等)
