class Helper:
    def __init__(self, app):
        self._bot = app._bot
    
    async def get_all_guilds()