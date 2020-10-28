from kivy.app import App

from kivy.uix.recycleview import RecycleView

from kivy.lang import Builder
#from kivy.uix.screenmanager import ScreenManager, Screen
#from kivy.uix.button import Button


KV = """
<RV>: 
	viewclass: 'Button' # defines the viewtype for the data items. 
	orientation: "vertical"
	spacing: 40
	padding:10, 10
	space_x: self.size[0]/3

	RecycleBoxLayout: 
		color:(0, 0.7, 0.4, 0.8) 
		default_size: None, dp(56) 

		# defines the size of the widget in reference to width and height 
		default_size_hint: 0.4, None
		
        size_hint_y: None
        height: self.minimum_height 
        orientation: 'vertical' # defines the orientation of data items
"""
Builder.load_string(KV)
class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        #super().__init__(**kwargs)
        self.data = [{'text': str(x) for x in range(20)}]


"""
Builder.load_string('''
<RV>:
    viewclass: 'Label'
    RecycleBoxLayout:
        default_size: None, dp(56)
        default_size_hint: 1, None
        size_hint_y: None
        height: self.minimum_height
        orientation: 'vertical'
''')

class RV(RecycleView):
    def __init__(self, **kwargs):
        #super(RV, self).__init__(**kwargs)
        super().__init__(**kwargs)
        self.data = [{'text': str(x)} for x in range(100)]

"""
class TestApp(App):
    def build(self):
        return RV()

if __name__ == '__main__':
    TestApp().run()