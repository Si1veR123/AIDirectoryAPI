from django.apps import AppConfig

class ToolConfig(AppConfig):
    name = 'tool'

    def ready(self):
        import tool.signals
