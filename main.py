import uuid
import pandas as pd
import os, sys
from datetime import datetime
from kivymd.toast import toast
import requests
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import RoundedRectangle
from kivy.resources import resource_add_path
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivy.clock import Clock, mainthread
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
import kivymd_extensions.akivymd
from kivymd.uix.dialog import MDDialog
from android.permissions import Permission, request_permissions
################################################################################################
## EventDispatcher #############################################################################
################################################################################################
from kivymd.uix.label import MDLabel, MDIcon
import os
import re


class FailedLoginScreen(Screen):
    pass


class Movesdatas(EventDispatcher):
    """ element to dispatch between class """
    userid = StringProperty()
    bid = StringProperty()
    dates = StringProperty()
    depart = StringProperty()
    end = StringProperty()
    distance = StringProperty()
    volume = StringProperty()
    id_bx_deal = StringProperty()
    low_bid = StringProperty()
    etgd = StringProperty()
    etga = StringProperty()
    opt = StringProperty()
    bids = StringProperty()

    # evdispatch_data_list = ['bid','dates','depart','end','distance','volume','id_bx_deal','low_bid',]

    def __init__(self, **kwargs):
        super(Movesdatas, self).__init__(**kwargs)


################################################################################################
## BoxLayout ###################################################################################
################################################################################################


class Banner(FloatLayout):

    def __init__(self, movesdatas, **kwargs):
        super().__init__(**kwargs)
        self.movesdatas = movesdatas
        self.kv_contents()

    def kv_contents(self, **kwargs):
        with self.canvas.before:
            Color(rgba=(192 / 252, 245 / 255, 250 / 255, 1))
            self.rect = RoundedRectangle(radius=[(10.0, 10.0), (10.0, 10.0), (10.0, 10.0), (10.0, 10.0)])
            self.bind(pos=self.update_rect, size=self.update_rect)

        self.bid_button = Button(on_release=self.go_to_popupinfos,
                                 size=(40, 40), size_hint=(None, None), background_down='ressource/button_gobid_v.png',
                                 background_normal='ressource/button_gobid.png',
                                 pos_hint={"center_x": .25, "center_y": .2}, halign='center')

        self.picture_button = Button(on_release=self.go_to_popuppicture, size=(40, 40), size_hint=(None, None),
                                     background_down='ressource/button_go_pics__v.png',
                                     background_normal='ressource/button_go_pics.png',
                                     pos_hint={"center_x": .75, "center_y": .2}, halign='center')

        self.my_bid_volume = MDLabel(text=str(self.movesdatas.volume),
                                     pos_hint={"center_x": .75, "top": .8}, size_hint=(.3, .3),
                                     theme_text_color="Primary", bold=True, font_style="Overline", halign="center")

        self.my_bid_dates = MDLabel(text=self.movesdatas.dates,
                                    pos_hint={"center_x": .25, "top": .8}, size_hint=(.3, .3),
                                    theme_text_color="Primary", bold=True, font_style="Overline", halign="center")

        self.my_bid_distance = MDLabel(text=str(self.movesdatas.distance),
                                       pos_hint={"center_x": .5, "top": .8}, size_hint=(.3, .3),
                                       theme_text_color="Primary", bold=True, font_style="Overline", halign="center")

        self.my_bid_depart = MDLabel(text=self.movesdatas.depart,
                                     pos_hint={"center_x": .25, "center_y": .5}, size_hint=(.3, .5),
                                     theme_text_color="Primary", bold=True, font_style="Overline", halign="center")

        self.icon_truck = MDIcon(pos_hint={"center_x": .5, "center_y": .5}, halign="center", size_hint=(.3, .5),
                                 icon="truck-fast-outline")

        self.my_bid_end = MDLabel(text=self.movesdatas.end,
                                  pos_hint={"center_x": .75, "center_y": .5}, size_hint=(.3, .5),
                                  theme_text_color="Primary", bold=True, font_style="Overline", halign="center")

        self.id_bx_deal = MDLabel(text=self.movesdatas.id_bx_deal, disabled=True, size_hint_x=0, opacity=0)
        self.my_bid_label_table = MDLabel(text=self.movesdatas.bid, disabled=True, size_hint_x=0, opacity=0)

        self.add_widget(self.my_bid_volume)
        self.add_widget(self.my_bid_dates)
        self.add_widget(self.my_bid_distance)
        self.add_widget(self.my_bid_depart)
        self.add_widget(self.icon_truck)
        self.add_widget(self.my_bid_end)
        self.add_widget(self.id_bx_deal)
        self.add_widget(self.my_bid_label_table)
        self.add_widget(self.bid_button)
        self.add_widget(self.picture_button)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def go_to_popupinfos(self, movesdatas):
        popup_infos = PopupInfos(self.movesdatas)
        popup_infos.open()

    def go_to_popuppicture(self, movesdatas):
        popuppicture = Popuppicture(self.movesdatas)
        popuppicture.open()


################################################################################################
## Popup #######################################################################################
################################################################################################

class PopupModification(Popup):

    def __init__(self, movesdatas, **kwargs):
        super().__init__(**kwargs)
        self.movesdatas = movesdatas
        self.dispatch_to_class_moves_data_modified()
        Clock.unschedule(self.dispatch_to_class_moves_data_modified())
        self.sens = ''

    def my_bid_to_down(self):
        self.movesdatas.bids = self.movesdatas.bid
        self.ids['my_bid'].text = self.movesdatas.bids  ## lowest bid replace with low_bid
        self.movesdatas.bind(bids=self.ids['my_bid'].setter('text'))

    def dispatch_to_class_moves_data_modified(self):

        self.ids['id_deal_awaiting_bx'].text = self.movesdatas.id_bx_deal
        self.movesdatas.bind(id_bx_deal=self.ids['id_deal_awaiting_bx'].setter('text'))

        self.ids['my_bid'].text = self.movesdatas.bid  ## lowest bid replace with low_bid
        self.movesdatas.bind(bid=self.ids['my_bid'].setter('text'))

    def now_time_on_popup_mybid(self):
        self.now = datetime.now().time()

    def _on_press(self, button):
        try:
            self.sens = button
            Clock.schedule_interval(self.change_bid, .1)
        except ValueError:
            pass

    def _on_release(self):
        try:
            Clock.unschedule(self.change_bid)
        except ValueError:
            pass

    def change_bid(self, *args):
        try:
            number = int(self.movesdatas.bid)
            if self.sens == 'up':
                if number < 10000:
                    number += 50

            elif self.sens == 'down':
                if number > 1000:  ## nous pouvons setup un paramètre pour régulée.
                    number -= 100
            self.movesdatas.bid = str(number)
        except ValueError:
            pass

    ## Add methode to count no of user bid for limit
    def savebid(self, job):
        r = requests.get(
            "http://127.0.0.1:5000/biddata?iddealkv=" + str(self.movesdatas.id_bx_deal) + "&iduserbx=" + str(
                Movesdatas.userid) + "&biduser=" + str(job))

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class PopupInfos(Popup):

    def __init__(self, movesdatas, **kwargs):
        super().__init__(**kwargs)
        self.movesdatas = movesdatas
        self.dispatch_to_class_moves_data_detail_view()

    def dispatch_to_class_moves_data_detail_view(self):
        self.ids['my_bid_label'].text = self.movesdatas.bids
        self.movesdatas.bind(bids=self.ids['my_bid_label'].setter('text'))

        self.ids['my_depart_label'].text = self.movesdatas.depart
        self.movesdatas.bind(depart=self.ids['my_depart_label'].setter('text'))

        self.ids['my_end_label'].text = self.movesdatas.end
        self.movesdatas.bind(end=self.ids['my_end_label'].setter('text'))

        self.ids['my_distance_label'].text = self.movesdatas.distance
        self.movesdatas.bind(distance=self.ids['my_distance_label'].setter('text'))

        self.ids['my_volume_label'].text = self.movesdatas.volume
        self.movesdatas.bind(volume=self.ids['my_volume_label'].setter('text'))

        self.ids['my_dates_label'].text = self.movesdatas.dates
        self.movesdatas.bind(dates=self.ids['my_dates_label'].setter('text'))

        self.ids['id_deal_awaiting'].text = self.movesdatas.id_bx_deal
        self.movesdatas.bind(id_bx_deal=self.ids['id_deal_awaiting'].setter('text'))

        self.ids['my_bid_label'].text = self.movesdatas.bids
        self.movesdatas.bind(bids=self.ids['my_bid_label'].setter('text'))

        self.ids['etg_depart'].text = self.movesdatas.etgd
        self.movesdatas.bind(etgd=self.ids['etg_depart'].setter('text'))

        self.ids['etg_arrive'].text = self.movesdatas.etga
        self.movesdatas.bind(etga=self.ids['etg_arrive'].setter('text'))

        self.ids['option_dem'].text = self.movesdatas.opt
        self.movesdatas.bind(opt=self.ids['option_dem'].setter('text'))

    def go_to_bid_popup(self):
        popup_modification = PopupModification(self.movesdatas)
        popup_modification.open()

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Popuppicture(Popup):

    def __init__(self, movesdatas, **kwargs):
        super().__init__(**kwargs)
        self.movesdatas = movesdatas
        self.add_buttons()
        with self.canvas.before:
            Color(rgba=(0, 0, 0, 0))
            self.rect = RoundedRectangle(radius=[(10.0, 10.0), (10.0, 10.0), (10.0, 10.0), (10.0, 10.0)])
            self.bind(pos=self.update_rect, size=self.update_rect)

    def add_buttons(self):

        self.box = self.ids.box

        try:

            r = requests.get("http://127.0.0.1:5000/picsdata?iddealkv=" + str(self.movesdatas.id_bx_deal))

            rcontent = str(r.content)

            rcontent = rcontent.replace('"', '')
            rcontent = rcontent.replace('[', '')
            rcontent = rcontent.replace(']', '')
            rcontent = rcontent.split('), (')

            list_link_mimage_move = []

            for row in rcontent:
                idurl = re.search("(?P<url>https?://[^\s]+)", row).group("url")
                idurl = idurl.replace("'", "")
                idurl = idurl.replace(",", "")
                list_link_mimage_move.append(idurl)

            lenght_records = len(list_link_mimage_move)
            imagepath = (str(self.movesdatas.id_bx_deal))

            if not os.path.exists(imagepath):
                os.makedirs(imagepath)
                pass

            for row, i in zip(list_link_mimage_move, range(lenght_records)):
                if not os.path.isfile(str(imagepath) + '/Prodemenageur_move_image' + (str(str(i)) + '.jpg')):
                    image_url = str(row)
                    img_data = requests.get(str(image_url)).content
                    with open(str(imagepath) + '/Prodemenageur_move_image' + (str(str(i)) + '.jpg'), 'wb')as handler:
                        handler.write(img_data)
                        self.box.add_widget(Button(
                            background_normal=(str(imagepath) + '/Prodemenageur_move_image' + (str(str(i)) + '.jpg'))))
                    pass
                if os.path.isfile(str(imagepath) + '/Prodemenageur_move_image' + (str(str(i)) + '.jpg')):
                    self.box.add_widget(Button(
                        background_normal=(str(imagepath) + '/Prodemenageur_move_image' + (str(str(i)) + '.jpg'))))
                    pass

        except Exception:
            print("Error")

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


################################################################################################
## SCREEN ######################################################################################
################################################################################################
class ScreenTest(Screen):
    def build(self):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.grid_test = self.ids['grid_test']
        self.add_widgets_with_sqlconnection()

    def refreshdata(self):
        self.clearwidget_scrollview()
        self.add_widgets_with_sqlconnection()

    def clearwidget_scrollview(self):
        self.grid_test.clear_widgets()

    def close_application(self):
        # closing application
        self.manager.get_screen("login")
        self.manager.current = 'login'

    def add_widgets_with_sqlconnection(self):
        r = requests.get("http://127.0.0.1:5000/movesdata")

        rcontent = r.content
        rcontent = str(r.content)
        rcontent = rcontent.replace('"', '')
        rcontent = rcontent.replace('[', '')
        rcontent = rcontent.replace(']', '')
        rcontent = rcontent.replace('datetime.date', '')

        rcontent = rcontent.split('), (')

        for row in rcontent:
            movesdatas = Movesdatas()

            movesdatas.bid = str('3000')

            delimiters = "', ", "), "
            regexPattern = '|'.join(map(re.escape, delimiters))
            row_element = re.split(regexPattern, row)

            idbxdeal = row_element[0]
            idbxdeal = idbxdeal.replace("'", "")
            idbxdeal = idbxdeal.replace("(", "")
            idbxdeal = idbxdeal.replace("b", "")
            movesdatas.id_bx_deal = str(idbxdeal)

            date_row = row_element[1]
            date_row = date_row.replace('(', '')
            date_row = date_row.replace(', ', '-')
            datemove = date_row
            movesdatas.dates = str(datemove)

            ville_depart = row_element[2]
            ville_depart = ville_depart.replace("'", "")
            ville_depart = ville_depart.replace(", Morocco", "")
            movesdatas.depart = str(ville_depart)

            ville_darrivee = row_element[3]
            ville_darrivee = ville_darrivee.replace("'", "")
            ville_darrivee = ville_darrivee.replace(", Morocco", "")
            movesdatas.end = str(ville_darrivee)

            distance = row_element[4]
            distance = distance.replace("'", "")
            movesdatas.distance = str(distance)

            volume = row_element[5]
            volume = volume.replace("'", "")
            movesdatas.volume = volume

            Etage_d = row_element[6]
            Etage_d = Etage_d.replace("'", "")
            Etage_d = re.sub(r'\\xc3\\xa8me', 'ème', Etage_d)
            Etage_d = re.sub(r'\\xc3\\xa9tage', 'étage', Etage_d)
            movesdatas.etgd = str(Etage_d)

            Etage_a = row_element[7]
            Etage_a = Etage_a.replace("'", "")
            Etage_a = re.sub(r'\\xc3\\xa8me', 'ème', Etage_a)
            Etage_a = re.sub(r'\\xc3\\xa9tage', 'étage', Etage_a)
            movesdatas.etga = str(Etage_a)

            option = row_element[8]
            option = option.replace("'", "")
            option = option.replace(")", "")
            option = re.sub(r'd\\xc3\\xa9chargement', 'déchargement', option)
            option = re.sub(r'd\\xc3\\xa9montage', 'démontage', option)
            movesdatas.opt = str(option)

            wid = Banner(movesdatas)
            self.grid_test.add_widget(wid)


class LoginScreen(Screen):

    def build(self):
        pass

    def save_username(self):
        Movesdatas.userid = self.ids.usernamevalue.text
        print(Movesdatas.userid)

    def login_button_action(self):

        try:
            input_email = self.ids.usernamevalue.text
            input_password = self.ids.passwordvalue.text
            r = requests.get(
                "http://127.0.0.1:5000/login?passwordi=" + str(input_password) + "&username=" + str(input_email))
            response = str(r.content)
            response = response.replace("'", "")
            response = response.replace("b", "")

            if response != 'ok':
                toast('Invalid Login/Password')
                self.manager.current = 'failedlogin'

            # else, if valid
            else:
                toast('Login and Password are correct!')
                self.save_username()
                user_screen = self.manager.get_screen("test")
                user_screen._userid = self.ids.usernamevalue.text
                self.manager.current = 'test'
                # update last_login column
            pass

        except Exception:
            print('error')


################################################################################################
## APPs ########################################################################################
################################################################################################

class MainApp(MDApp):
    """App Principale"""

    def callback(permission, results):
        if all([res for res in results]):
            print("got all permissions")
        else:
            print("Did not get all permissions")

    request_permissions([Permission.INTERNET, Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

    def build(self):
        """Construction de l'App principale"""
        Builder.load_file('mainaaa.kv')
        self.theme_cls.primary_palette = "Yellow"
        self.theme_cls.primary_hue = "700"
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(FailedLoginScreen(name='failedlogin'))
        self.sm.add_widget(ScreenTest(name='test'))
        self.sm.transition = SlideTransition(direction='left')
        return self.sm

    def navigation_draw(self):
        print("Navigation")


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MainApp().run()