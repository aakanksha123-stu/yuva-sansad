import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from voting.consumers import VoteConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuva_sansad.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": URLRouter([
        path("ws/vote/", VoteConsumer.as_asgi()),
    ]),
})