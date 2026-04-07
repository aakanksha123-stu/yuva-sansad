import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from voting.consumers import VoteConsumer  # Make sure 'voting' is in backend

# Set the settings module correctly for backend folder
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yuva_sansad.settings')

# Standard Django ASGI application
django_asgi_app = get_asgi_application()

# Channels routing for WebSockets
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Handles regular HTTP requests

    "websocket": URLRouter([
        path("ws/vote/", VoteConsumer.as_asgi()),  # WebSocket route
    ]),
})