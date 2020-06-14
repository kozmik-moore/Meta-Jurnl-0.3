# from kivy.app import App

from kivy.config import Config

Config.set('kivy','window_icon','graph_icon.png')
Config.set('graphics', 'width', '1540')
Config.set('graphics', 'height', '810')


from app_widgets import JournalApp

app = JournalApp()
app.run()
