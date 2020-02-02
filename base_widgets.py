from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.togglebutton import ToggleButton

from community_widgets import AlignedTextInput

Builder.load_file('base-widgets.kv')


class GenericScreen(Screen):
    pass


class GenericInput(TextInput):
    pass


class GenericAlignedTextInput(GenericInput, AlignedTextInput):
    pass


class GenericLabel(Label):
    pass


class GenericButton(Button):
    pass


class GenericToggleButton(ToggleButton):
    pass


class GenericRecycleView(RecycleView):
    pass


class GenericSlider(Slider):
    pass
