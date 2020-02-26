import asyncio
import inspect
import uvicorn

from fastapi import FastAPI

class App:
    def __init__(self, **kwargs):
        self.bot = kwargs.get("bot")
        self.bot.dashboard_routes = {}
        
        self.app = FastAPI()
        self.app.bot = self.bot
        
        self.port = kwargs.get("port", 5000)
        
    def route(self, *args, **kwargs):
        def wrapper(func):
            route = kwargs.get("route")
            methods = kwargs.get("methods", ["GET"])
            callback = func
            
            if not isinstance(methods, list):
                raise ValueError("Rote methods must be a list.")
            
            if not route:
                route = "/%s" % func.__name__
            if not route.startswith("/"):
                raise ValueError("Routes must start with '/'.")
            
            if not inspect.iscoroutinefunction(func):
                raise ValueError("Rote callback must be a coroutine.")
            
            self.bot.dashboard_routes[route] = (route, callback, methods)
            print("Added route %s to routes." % route)
        return wrapper

    def add_url(self, path, callback, methods: list = None):
        if not inspect.iscoroutinefunction(callback):
            raise ValueError("Callback must be a coroutine.")
        
        self.app.add_route(path, callback, methods, include_in_schema=True, name=path)
        
    def run(self):
        self.bot.dispatch("on_dashcord_start", "Starting on PORT %d" % self.port)
        
        for route in self.bot.dashboard_routes:
            print(route)
        return uvicorn.run(self.app, port=self.port)