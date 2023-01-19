import ctypes
import itertools
import random
import threading
from copy import deepcopy
from math import factorial

import app
import poker_combinations as pc


threads = []
threads_to_stop = 0
thread_in_process = False


class ThreadWithException(threading.Thread):
    def __init__(self, mainLayout):
        threading.Thread.__init__(self)
        self.mainLayout = mainLayout

    def run(self):
        start_calculator(self.mainLayout)

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id_, thread in threading._active.items():
            if thread is self:
                return id_

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


def change_ui_state(mainLayout, text, chances=None):
    mainLayout.children[3].text = text
    if chances is not None:
        for i in range(len(chances)):
            mainLayout.children[1].children[i].children[3].text = 'EQT: ' + str(round(chances[i][0] * 100, 2)) + '%'
            mainLayout.children[1].children[i].children[2].text = 'WIN: ' + str(round(chances[i][1] * 100, 2)) + '%'
            mainLayout.children[1].children[i].children[1].text = 'SPL: ' + str(round(chances[i][2] * 100, 2)) + '%'


def create_calculating_thread(mainLayout):
    #global thread_in_process
    #if thread_in_process:
    #    global threads_to_stop
    #    threads_to_stop += 1
    #thread_in_process = True
    for thread in threads:
        thread.raise_exception()
        thread.join()
    threads.clear()
    threads.append(ThreadWithException(mainLayout))
    threads[0].start()


def start_calculator(mainLayout):
    DECK_SIZE = 52
    board = []
    hands = []
    discarded = []

    for card in mainLayout.children[2].children:
        board.append(card.card_id)

    for hand_grid in mainLayout.children[1].children:
        hand = [hand_grid.children[4].children[0].card_id, hand_grid.children[4].children[1].card_id]
        hands.append(hand)

    fixed_cards = get_fixed_cards(board + sum(hands, []) + discarded)

    N = DECK_SIZE - len(fixed_cards)
    K = 5 - len(get_fixed_cards(board))
    board_options = factorial(N) / (factorial(K) * factorial(N - K))
    N -= K
    K = 2 * len(hands) - len(get_fixed_cards(sum(hands, [])))
    hands_options = factorial(N) / factorial(N - K)
    max_counter = board_options * hands_options

    rough_calculated = False
    killed = False
    if max_counter > 400_000:
        rough_calculated = True
        killed = calculate_rough_chances(board, hands, fixed_cards, mainLayout)
    if not killed:
        calculate_exact_chances(board, hands, discarded, fixed_cards, max_counter, rough_calculated, mainLayout)


def deck_init(fixed_cards, DECK_SIZE):
    deck = [False] * DECK_SIZE
    for card_id in fixed_cards:
        deck[card_id] = True
    return deck


def get_fixed_cards(cards):
    fixed_cards = []
    for card_id in cards:
        if card_id is not None:
            fixed_cards.append(card_id)
    return fixed_cards


def get_combinations(deck, N_of_cards_to_permute):
    f_indexes = [i for i, x in enumerate(deck) if not x]
    return [list(x) for x in itertools.combinations(f_indexes, N_of_cards_to_permute)]


def insert_cards(board_or_hands, cards_to_insert):
    cards = board_or_hands.copy()
    iterator = 0
    if not isinstance(cards[0], list):
        for i in range(len(cards)):
            if cards[i] is None:
                cards[i] = cards_to_insert[iterator]
                iterator += 1
    else:
        for i in range(len(cards)):
            if cards[i][0] is None:
                cards[i][0] = cards_to_insert[iterator]
                iterator += 1
            if cards[i][1] is None:
                cards[i][1] = cards_to_insert[iterator]
                iterator += 1
    return cards


def clarify_winner(hands_with_max_combination, combinations):
    for i in range(5):
        best_rank = 0
        hands_with_best_rank = []
        for j in range(len(hands_with_max_combination)):
            if combinations[hands_with_max_combination[j]][2][i] % 13 > best_rank:
                best_rank = combinations[hands_with_max_combination[j]][2][i] % 13
                hands_with_best_rank = [hands_with_max_combination[j]]
            elif combinations[hands_with_max_combination[j]][2][i] % 13 == best_rank:
                hands_with_best_rank.append(hands_with_max_combination[j])
        if len(hands_with_best_rank) == 1:
            return hands_with_best_rank
        hands_with_max_combination = hands_with_best_rank
    return hands_with_max_combination


def get_showdown_result(board, hands):
    # hands won, hands split
    combinations = []

    for hand in hands:
        combinations.append(pc.check_combination(board, hand))

    max_combination = 0
    hands_with_max_combination = []
    for i in range(len(combinations)):
        if combinations[i][1] > max_combination:
            max_combination = combinations[i][1]
            hands_with_max_combination = [i]
        elif combinations[i][1] == max_combination:
            hands_with_max_combination.append(i)

    if len(hands_with_max_combination) == 1:
        return [[hands_with_max_combination[0]], []]
    hands_with_max_combination = clarify_winner(hands_with_max_combination, combinations)
    if len(hands_with_max_combination) == 1:
        return [[hands_with_max_combination[0]], []]
    return [[], hands_with_max_combination]


def random_fill(cards, deck):
    for i in range(len(cards)):
        if cards[i] is None:
            while True:
                random_card = random.randint(0, len(deck) - 1)
                if deck[random_card]:
                    continue
                deck[random_card] = True
                cards[i] = random_card
                break


def calculate_rough_chances(board, hands, fixed_cards, mainLayout):
    DECK_SIZE = 52
    board_saved = board.copy()
    hands_saved = deepcopy(hands)
    max_counter = 100_000
    counter = 0
    times = []
    for i in range(len(hands)):
        times.append([0, 0, 0])  # equ, win, split

    global threads_to_stop
    while counter < max_counter:
        counter += 1
        board = board_saved.copy()
        hands = deepcopy(hands_saved)
        deck = deck_init(fixed_cards, DECK_SIZE)
        random_fill(board, deck)
        for i in range(len(hands)):
            random_fill(hands[i], deck)

        result = get_showdown_result(board, hands)
        for k in result[0]:
            times[k][0] += 1
            times[k][1] += 1
        for k in result[1]:
            times[k][0] += 1 / len(result[1])
            times[k][2] += 1

        if (counter + 1) % 982 == 0 and threads_to_stop:
            threads_to_stop -= 1
            return
        if (counter + 1) % 5000 == 0:
            chances = deepcopy(times)
            for k in range(len(chances)):
                chances[k][0] /= counter
                chances[k][1] /= counter
                chances[k][2] /= counter
            text = 'Calculating random subset... ' + str(round(counter / max_counter * 100, 1)) + '%'
            change_ui_state(mainLayout, text, chances)
    if threads_to_stop:
        threads_to_stop -= 1
        return True
    return False


def calculate_exact_chances(board, hands, discarded, fixed_cards, max_counter, rough_calculated, mainLayout):
    DECK_SIZE = 52
    deck = deck_init(fixed_cards, DECK_SIZE)
    board_saved = board.copy()
    hands_saved = deepcopy(hands)
    counter = 0
    times = []
    for i in range(len(hands)):
        times.append([0, 0, 0])  # equ, win, split
    global threads_to_stop

    N_of_cards_to_permute = 5 - len(get_fixed_cards(board_saved))
    for i in get_combinations(deck, N_of_cards_to_permute):
        deck = deck_init(fixed_cards + i, DECK_SIZE)
        board = insert_cards(board_saved.copy(), i)

        N_of_cards_to_permute = 2 * len(hands_saved) - len(get_fixed_cards(sum(hands_saved, [])))
        for j in get_combinations(deck, N_of_cards_to_permute):
            for m in itertools.permutations(j):
                counter += 1
                hands = insert_cards(deepcopy(hands_saved), m)
                result = get_showdown_result(board, hands)
                for k in result[0]:
                    times[k][0] += 1
                    times[k][1] += 1
                for k in result[1]:
                    times[k][0] += 1 / len(result[1])
                    times[k][2] += 1
                if (counter + 1) % 982 == 0 and threads_to_stop:
                    threads_to_stop -= 1
                    return
                if (counter + 1) % 5000 == 0:
                    chances = deepcopy(times)
                    for k in range(len(chances)):
                        chances[k][0] /= counter
                        chances[k][1] /= counter
                        chances[k][2] /= counter
                    app.print_state(board_saved, hands_saved, discarded, chances, counter / max_counter * 100)

                    text = 'Calculating... ' + str(round(counter / max_counter * 100, 1)) + '%'
                    if rough_calculated:
                        chances = None
                    change_ui_state(mainLayout, text, chances)

    if threads_to_stop:
        threads_to_stop -= 1
        return
    global thread_in_process
    thread_in_process = False
    text = 'Calculation Finished.'
    change_ui_state(mainLayout, text)

    for i in range(len(times)):
        times[i][0] /= counter
        times[i][1] /= counter
        times[i][2] /= counter

    return times
