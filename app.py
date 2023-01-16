import poker_calculator as calculator

suit_pack = ['♠', '♥', '♦', '♣']
rank_pack = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
DECK_SIZE = len(suit_pack) * len(rank_pack)


def parse_cards(cards):
    s = ''
    for card_id in cards:
        if card_id is not None:
            s += get_card(card_id) + ' '
        else:
            s += '__ '
    return s


def get_card(card_id):
    return rank_pack[card_id % len(rank_pack)] + suit_pack[card_id // len(rank_pack)]


def print_cards_left(deck):
    for i in range(len(suit_pack)):
        for j in range(len(rank_pack)):
            if not deck[i * len(rank_pack) + j]:
                print(get_card(i * len(rank_pack) + j), end=' ')
            else:
                print('__', end=' ')
        print()


def print_state(board, hands, discarded, chances, progress=100):
    for _ in range(20):
        print()
    print('\tBoard:')
    for card_id in board:
        if card_id is not None:
            print(get_card(card_id), end=' ')
        else:
            print('__', end=' ')
    print()

    print()
    for i in range(len(hands)):
        print('\t' + parse_cards(hands[i]))
        print('Equity:\t' + str(round(chances[i][0] * 100, 2)) + '%')
        print('Win:\t' + str(round(chances[i][1] * 100, 2)) + '%')
        print('Split:\t' + str(round(chances[i][2] * 100, 2)) + '%')
    print()

    print('Discarded cards:')
    if len(discarded) == 0:
        print('None', end=' ')
    else:
        for card_id in discarded:
            print(get_card(card_id), end=' ')
    print()

    print()
    if progress != 100:
        print('Still checking all combinations...')
        print('Progress: ' + str(round(progress, 2)) + '%')
    else:
        print('All combinations checked, the result is exact.')


def start():
    board = [1, 49, 39, None, None]
    hands = [[None, 25], [31, 32], [50, None]]
    discarded = [3, 4]

    while True:
        chances = calculator.calculate_chances(board, hands, discarded, suit_pack, rank_pack)
        # print_state(board, hands, discarded, chances)
        print_state(board, hands, discarded, chances)
        n = int(input())
