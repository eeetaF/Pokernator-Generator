import itertools
from copy import deepcopy
import poker_combinations as pc
import app
from math import factorial


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


def calculate_chances(board, hands, discarded, suit_pack, rank_pack):
    fixed_cards = get_fixed_cards(board + sum(hands, []) + discarded)
    DECK_SIZE = len(suit_pack) * len(rank_pack)
    deck = deck_init(fixed_cards, DECK_SIZE)
    board_saved = board.copy()
    hands_saved = deepcopy(hands)

    N = DECK_SIZE - len(fixed_cards)
    K = 5 - len(get_fixed_cards(board))
    board_options = factorial(N) / (factorial(K) * factorial(N - K))
    N -= K
    K = 2 * len(hands) - len(get_fixed_cards(sum(hands, [])))
    hands_options = factorial(N) / factorial(N - K)
    max_counter = board_options * hands_options
    counter = 0

    times = []
    for i in range(len(hands)):
        times.append([0, 0, 0])  # equ, win, split

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
                if (counter - 10000) % 60000 == 0:
                    chances = deepcopy(times)
                    for k in range(len(chances)):
                        chances[k][0] /= counter
                        chances[k][1] /= counter
                        chances[k][2] /= counter
                    app.print_state(board_saved, hands_saved, discarded, chances, counter / max_counter * 100)

    for i in range(len(times)):
        times[i][0] /= counter
        times[i][1] /= counter
        times[i][2] /= counter

    return times
