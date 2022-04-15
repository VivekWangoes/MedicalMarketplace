from django.urls import re_path

from . import consumer
# from . import chat_consumers

websocket_urlpatterns = [
    re_path(r'ws/video/(?P<room_name>\w+)/$', consumer.VideoCallSignalConsumer),
    # re_path(r'ws/chat-message/(?P<room_name>\w+)/$', chat_consumers.ChatConsumer),
]
