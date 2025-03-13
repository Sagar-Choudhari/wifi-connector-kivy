from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.clock import Clock
from wifi_manager import WiFiManager

class WifiScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wifi = WiFiManager()
        self.password = None
        Clock.schedule_once(lambda dt: self.rescan_networks())

    def rescan_networks(self):
        self.ids.network_list.clear_widgets()
        networks = self.wifi.scan_networks()
        for net in networks:
            btn = Button(
                text=f"{net.get('ssid', 'Hidden')} - {'Secured' if net.get('secured') else 'Open'}",
                size_hint_y=None,
                height=44
            )
            btn.net_info = net
            btn.bind(on_press=self.show_connection_dialog)
            self.ids.network_list.add_widget(btn)

    def show_connection_dialog(self, instance):
        net = instance.net_info
        content = BoxLayout(orientation='vertical', spacing=10)
        
        if net.get('secured'):
            self.password = TextInput(hint_text='Password', password=True)
            content.add_widget(self.password)
        else:
            content.add_widget(Label(text='Open network - No password needed'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=5)
        connect_btn = Button(text='Connect')
        connect_btn.bind(on_press=lambda x: self.start_connection(net))
        btn_layout.add_widget(connect_btn)
        btn_layout.add_widget(Button(
            text='Cancel',
            on_press=lambda x: self.popup.dismiss()
        ))
        content.add_widget(btn_layout)
        
        self.popup = Popup(
            title=f"Connect to {net.get('ssid', 'Unknown')}",
            content=content,
            size_hint=(0.8, 0.4)
        )
        self.popup.open()


    def start_connection(self, net):
        
        if self.popup:
            self.popup.dismiss()
        
        # Get credentials first
        password = self.password.text if net.get('secured') else None
        
        # Show loading popup immediately
        self.show_loading_popup()
        
        # Start connection in background thread
        self.wifi.connect_to_network(
            net['ssid'],
            password,
            lambda success, msg: Clock.schedule_once(
                lambda dt: self.show_connection_result(success, msg)
            )
        )


    def show_loading_popup(self):
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        content.add_widget(Label(text='Connecting...'))
        self.loading_popup = Popup(
            title='Please wait',
            content=content,
            size_hint=(0.6, 0.3),
            auto_dismiss=False
        )
        self.loading_popup.open()


    def show_connection_result(self, success, message):
        # Dismiss loading popup first
        if self.loading_popup:
            self.loading_popup.dismiss()
        
        # Show result popup
        content = BoxLayout(orientation='vertical', spacing=10)
        content.add_widget(Label(text=message))
        content.add_widget(Button(
            text='OK',
            size_hint_y=None,
            height=50,
            on_press=lambda x: self.result_popup.dismiss()
        ))
        
        self.result_popup = Popup(
            title='Connection Status',
            content=content,
            size_hint=(0.6, 0.3)
        )
        self.result_popup.open()
        
        
class WifiApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(WifiScreen(name='wifi'))
        return sm

if __name__ == '__main__':
    WifiApp().run()
    
    
    
    