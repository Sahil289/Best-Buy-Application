from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen,ScreenManager,NoTransition,CardTransition
from myfirebase import MyFirebase
from kivy.animation import Animation
from kivy.factory import Factory
import requests
import json
from operator import itemgetter
from kivymd.toast import toast

class SigninScreen(Screen):
    pass
class SignupScreen(Screen):
	pass
class SearchScreen(Screen):
    pass
class DisplayScreen(Screen):
	pass



class Myapp(MDApp):
    my_id=1
    def __init__(self,**kwargs):
        self.theme_cls.theme_style="Light"
        self.theme_cls.primary_palette="Blue"
        self.sm=ScreenManager()
        super().__init__(**kwargs)
    
    def show_popup(self,mssg):
        toast(""+mssg)

    def change_screen(self,screen_name):
        screen_manager=self.root.ids['screen_manager']
        screen_manager.current=screen_name

    def animate_card(self, widget):
        anim=Animation(pos_hint={"center_y":0.6},duration=0.8)
        anim.start(widget)

    def animate_background(self, widget):
        anim=Animation(size_hint_y=1,duration=0.4)+Animation(size_hint_y=0.5,duration=0.4)
        anim.start(widget.ids.bx)
        
    def build(self):
        Gui=Builder.load_file("main.kv")
        self.sm.add_widget(Factory.SigninScreen(name="signin_screen"))
        self.my_firebase=MyFirebase()
        return Gui
    def on_start(self):
        try:
            with open("refresh_token.txt","r") as f:
                refresh_token=f.read()
                id_token,local_id=self.my_firebase.exchange_refresh_token(refresh_token)
            result=requests.get("https://bestbuydb-40d9e.firebaseio.com/" + local_id + ".json?auth=" + id_token)
            data=json.loads(result.content.decode())
            self.root.ids['screen_manager'].transition= NoTransition()
            self.change_screen("search_screen")
            self.root.ids['screen_manager'].transition= CardTransition()
        except Exception as e:
            pass
Myapp().run()