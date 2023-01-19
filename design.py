from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup


def add_hand_grid(parentLayout):
    handOutsideGrid = GridLayout(cols=1, rows=5, spacing=1)
    handInsideGrid = GridLayout(cols=2, rows=1, spacing=1)

    handInsideGrid.add_widget(SelectableCardButton())
    handInsideGrid.add_widget(SelectableCardButton())

    handOutsideGrid.add_widget(handInsideGrid)
    handOutsideGrid.add_widget(Label(text='Equity', size_hint=(1, 0.4)))
    handOutsideGrid.add_widget(Label(text='Win', size_hint=(1, 0.4)))
    handOutsideGrid.add_widget(Label(text='Split', size_hint=(1, 0.4)))
    handOutsideGrid.add_widget(RemoveButton())

    parentLayout.children[1].add_widget(handOutsideGrid)

    if len(parentLayout.children[1].children) == 9:
        return True
    return False


class StyledButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = 0.99, 0.99, 0.99, 1
        self.font_size = 30
        self.font_name = 'fonts/CARDC___.ttf'


class CardButton(StyledButton):
    suit_pack = ['}', '{', '[', ']']
    rank_pack = ['2', '3', '4', '5', '6', '7', '8', '9', '=', 'J', 'Q', 'K', 'A']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card_id = None
        self.rank = '?'
        self.suit = '?'
        self.text = self.rank + self.suit
        self.set_color()

    def set_color(self):
        if self.suit == '{' or self.suit == '[':
            self.color = 0.7, 0.08, 0.08, 1
            self.outline_color = 0, 0, 0, 1
            # self.outline_width = 1
        else:
            self.color = 0.1, 0.1, 0.1, 1
            self.outline_width = 0

    def set_rank_suit(self):
        if self.card_id is None:
            self.rank = '?'
            self.suit = '?'
            return
        self.rank = self.rank_pack[self.card_id % len(self.rank_pack)]
        self.suit = self.suit_pack[self.card_id // len(self.rank_pack)]

    def change_card(self, new_card_id):
        self.card_id = new_card_id
        self.set_rank_suit()
        self.text = self.rank + self.suit
        self.set_color()


class SelectableCardButton(CardButton):
    def on_release(self):
        popup_grid = GridLayout(cols=4, rows=14, size_hint=(1, 1))
        popup = Popup(title='Choose card:', content=popup_grid)

        for i in range(52):
            choosing_card_button = ChoosingCardButton()
            choosing_card_button.change_card(i * 13 % 51)
            if i == 51:
                choosing_card_button.change_card(51)
            choosing_card_button.bind(on_press=lambda x: self.change_card(x.card_id))
            choosing_card_button.set_popup(popup)
            popup_grid.add_widget(choosing_card_button)
        for i in range(4):
            choosing_card_button = ChoosingCardButton()
            choosing_card_button.change_card(None)
            choosing_card_button.bind(on_press=lambda x: self.change_card(x.card_id))
            choosing_card_button.set_popup(popup)
            popup_grid.add_widget(choosing_card_button)
        popup.open()


class ChoosingCardButton(CardButton):
    papa_popup = None

    def set_popup(self, popup):
        self.papa_popup = popup

    def on_release(self):
        self.papa_popup.dismiss()


class AddHandButton(StyledButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = '+'

    def on_release(self):
        self.disabled = add_hand_grid(self.parent.parent)


class RemoveButton(StyledButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = 'Remove'
        self.font_name = 'fonts/OpenSans-Regular.ttf'
        self.size_hint = (1, 0.9)
        self.font_size = 20

    def on_release(self):
        grid = self.parent.parent
        grid.parent.children[0].children[0].disabled = False
        grid.remove_widget(self.parent)


class PokerCalculatorApp(App):
    def build(self):
        Window.size = (1080 / 3, 1920 / 3)
        Window.clearcolor = (40 / 255, 44 / 255, 52 / 255, 1)
        mainLayout = FloatLayout()

        boardGrid = GridLayout(cols=5, size_hint=(0.9, 0.1), pos_hint={'top': 1 - (0.05 * 9 / 16), 'center_x': 0.5})
        mainLayout.add_widget(boardGrid)
        board_buttons = []
        for i in range(5):
            board_buttons.append(SelectableCardButton())
            boardGrid.add_widget(board_buttons[i])

        handsGrid = GridLayout(cols=3, rows=3, size_hint=(0.9, 0.72),
                               pos_hint={'top': 1 - (0.25 * 9 / 16), 'center_x': 0.5}, spacing=5)
        mainLayout.add_widget(handsGrid)

        menuGrid = GridLayout(cols=5, size_hint=(0.9, 0.1), pos_hint={'y': (0.05 * 9 / 16), 'center_x': 0.5})
        mainLayout.add_widget(menuGrid)

        add_hand_grid(mainLayout)
        add_hand_grid(mainLayout)

        menuGrid.add_widget(AddHandButton())

        return mainLayout
