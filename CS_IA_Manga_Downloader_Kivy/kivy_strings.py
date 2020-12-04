
# This string creates the manga input page
manga_input_kv_str = '''
<MangaSearchPage>
    MDTextField:
        id: SearchFieldID
        mode: "rectangle"
        hint_text: "Type in a manga"
        size_hint:(0.5,0.1)
        pos_hint:{'center_x': 0.5, 'center_y': 0.5}
        on_text_validate: root.get_manga_query_data()
        focused: True
'''

manga_display_kv_str = '''
<MangaCoverTile@SmartTileWithLabel>
    size_hint_y: None
    height: "240dp"

<RV>:
    manga_data: app.manga_data
	viewclass: 'MangaCoverTile' # defines the viewtype for the data items.
    #viewclass: 'MDRectangleFlatButton' # defines the viewtype for the data items.
	orientation: "vertical"
	spacing: 40, 40
	padding:10, 10
	space_x: self.size[0]/3
	
	RecycleGridLayout:
		cols:3
		default_size: None, dp(56) 
		# defines the size of the widget in reference to width and height 
		default_size_hint: 0.4, None

        size_hint_y: None
        height: self.minimum_height 
        orientation: 'vertical' # defines the orientation of data items
'''

settings_page_kv_str = '''
<SettingsInterface>:
    orientation: 'vertical'
    Button:
        text: 'open the settings!'
        font_size: 150
        on_release: app.open_settings()
'''