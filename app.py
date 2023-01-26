from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from poker_calculator import create_calculating_thread

deck = [False] * 52

mainLayout = FloatLayout()


def add_hand_grid():
    handOutsideGrid = GridLayout(cols=1, rows=5, spacing=1)
    handInsideGrid = GridLayout(cols=2, rows=1, spacing=1)

    handInsideGrid.add_widget(SelectableCardButton())
    handInsideGrid.add_widget(SelectableCardButton())
    handOutsideGrid.add_widget(handInsideGrid)

    eqtLabel = Label(text='EQT:', size_hint=(1, 0.4), font_name='fonts/OpenSans-Regular.ttf', valign='middle')
    eqtLabel.bind(size=eqtLabel.setter('text_size'))
    handOutsideGrid.add_widget(eqtLabel)

    winLabel = Label(text='WIN:', size_hint=(1, 0.4), font_name='fonts/OpenSans-Regular.ttf', valign='middle')
    winLabel.bind(size=winLabel.setter('text_size'))
    handOutsideGrid.add_widget(winLabel)

    splLabel = Label(text='SPL:', size_hint=(1, 0.4), font_name='fonts/OpenSans-Regular.ttf', valign='middle')
    splLabel.bind(size=splLabel.setter('text_size'))
    handOutsideGrid.add_widget(splLabel)

    handOutsideGrid.add_widget(RemoveButton())

    global mainLayout
    mainLayout.children[1].add_widget(handOutsideGrid)

    return len(mainLayout.children[1].children) == 9


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
        if self.suit in ['{', '[']:
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

    def set_card(self, new_card_id):
        self.card_id = new_card_id
        self.set_rank_suit()
        self.text = self.rank + self.suit
        self.set_color()

    def change_card(self, new_card_id):
        if self.card_id is not None:
            deck[self.card_id] = False
        if new_card_id is not None:
            deck[new_card_id] = True
        self.set_card(new_card_id)
        global mainLayout
        create_calculating_thread(mainLayout)


class SelectableCardButton(CardButton):
    def on_release(self):
        popup_grid = GridLayout(cols=4, rows=14, size_hint=(1, 1))
        popup = Popup(title='Choose card:', content=popup_grid)

        for i in range(52):
            iterator = i
            if i != 51:
                iterator = i * 13 % 51
            disabled = deck[iterator]
            if self.card_id is not None and iterator == self.card_id:
                disabled = False
            choosing_card_button = ChoosingCardButton(iterator, disabled=disabled)
            choosing_card_button.bind(on_press=lambda x: self.change_card(x.card_id))
            choosing_card_button.set_popup(popup)
            popup_grid.add_widget(choosing_card_button)
        for i in range(4):
            choosing_card_button = ChoosingCardButton()
            choosing_card_button.set_card(None)
            choosing_card_button.bind(on_press=lambda x: self.change_card(x.card_id))
            choosing_card_button.set_popup(popup)
            popup_grid.add_widget(choosing_card_button)
        popup.open()


class ChoosingCardButton(CardButton):
    def __init__(self, card_id=None, **kwargs):
        super().__init__(**kwargs)
        self.card_id = card_id
        self.set_rank_suit()
        self.text = self.rank + self.suit
        self.set_color()

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
        for hand_grid in self.parent.parent.children[1].children:
            hand_grid.children[0].disabled = False
        self.disabled = add_hand_grid()
        global mainLayout
        create_calculating_thread(mainLayout)
        


class DiscardCardsButton(StyledButton):
    def __init__(self, discard_cards_grid, **kwargs):
        super().__init__(**kwargs)
        self.discard_cards_popup = Popup(title='Choose discarded cards:', content=discard_cards_grid, size_hint=(0.9, 0.19))
        self.text = 'D'

    def on_release(self):
        self.discard_cards_popup.open()


class RemoveButton(StyledButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = 'Remove'
        self.font_name = 'fonts/OpenSans-Bold.ttf'
        # self.font_name = 'fonts/OpenSans-Regular.ttf'
        self.size_hint = (1, 0.6)
        self.font_size = 20
        self.color = 0.1, 0.1, 0.1, 1

    def on_release(self):
        global mainLayout
        mainLayout.children[0].children[0].disabled = False
        if self.parent.children[4].children[0].card_id is not None:
            deck[self.parent.children[4].children[0].card_id] = False
        if self.parent.children[4].children[1].card_id is not None:
            deck[self.parent.children[4].children[1].card_id] = False
        self.parent.parent.remove_widget(self.parent)
        if len(mainLayout.children[1].children) == 2:
            for hand_grid in mainLayout.children[1].children:
                hand_grid.children[0].disabled = True
        create_calculating_thread(mainLayout)


class PokerCalculatorApp(App):
    def build(self):
        Window.size = (1080 / 3, 1920 / 3)
        Window.clearcolor = (40 / 255, 44 / 255, 52 / 255, 1)
        global mainLayout

        calculatorStateLabel = Label(text='', size_hint=(1, 0.1),
                                     font_name='fonts/OpenSans-Bold.ttf', font_size=17, color=(0.9, 0.9, 0.9, 1),
                                     pos_hint={'y': 0.15, 'x': 0.07}, halign='left')
        calculatorStateLabel.bind(size=calculatorStateLabel.setter('text_size'))
        mainLayout.add_widget(calculatorStateLabel)

        boardGrid = GridLayout(cols=5, size_hint=(0.9, 0.1), pos_hint={'top': 1 - (0.05 * 9 / 16), 'center_x': 0.5})
        mainLayout.add_widget(boardGrid)
        board_buttons = []
        for i in range(5):
            board_buttons.append(SelectableCardButton())
            boardGrid.add_widget(board_buttons[i])

        handsGrid = GridLayout(cols=3, rows=3, size_hint=(0.9, 0.66),
                               pos_hint={'top': 1 - (0.25 * 9 / 16), 'center_x': 0.5}, spacing=5)
        mainLayout.add_widget(handsGrid)

        menuGrid = GridLayout(cols=5, size_hint=(0.9, 0.1), pos_hint={'y': (0.05 * 9 / 16), 'center_x': 0.5})
        mainLayout.add_widget(menuGrid)

        add_hand_grid()
        add_hand_grid()
        add_hand_grid()

        menuGrid.add_widget(AddHandButton())
        
        discard_cards_grid = GridLayout(cols=5, pos_hint={'center_x': 0.5}, size_hint=(0.9, 0.9))
        for _ in range(5):
            discard_cards_grid.add_widget(SelectableCardButton())
        menuGrid.add_widget(DiscardCardsButton(discard_cards_grid))

        create_calculating_thread(mainLayout)

        return mainLayout