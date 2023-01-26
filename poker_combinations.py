def check_combination(board, hand):
    cards = board + hand
    suit_sorted = sorted(cards, reverse=True)
    rank_sorted = sorted(cards, key=lambda x: x % 13, reverse=True)

    combination = check_royal(suit_sorted)
    if combination is not None:
        return combination
    combination = check_sf(suit_sorted)
    if combination is not None:
        return combination
    combination = check_quads(rank_sorted)
    if combination is not None:
        return combination
    combination = check_boat(rank_sorted)
    if combination is not None:
        return combination
    combination = check_flush(suit_sorted)
    if combination is not None:
        return combination
    combination = check_straight(rank_sorted)
    if combination is not None:
        return combination
    combination = check_set(rank_sorted)
    if combination is not None:
        return combination
    combination = check_two(rank_sorted)
    if combination is not None:
        return combination
    combination = check_pair(rank_sorted)
    if combination is not None:
        return combination
    return ['High', 0, rank_sorted[:5]]


def check_royal(cards):
    combination = ['Royal Flush', 9, []]
    start = True
    for i in range(7):
        if start is True and cards[i] % 13 == 12:
            start = False
            combination[2].append(cards[i])
        elif start is False and cards[i] == cards[i - 1] - 1:
            combination[2].append(cards[i])
        elif start is False and cards[i] % 13 == 12:
            combination[2] = [cards[i]]
        else:
            start = True
            combination[2] = []
        if len(combination[2]) == 5:
            return combination

    return None


def check_sf(cards):
    combination = ['Straight Flush', 8, [cards[0]]]
    for i in range(1, 7):
        if cards[i] == cards[i - 1] - 1 and cards[i] // 13 == cards[i - 1] // 13:
            combination[2].append(cards[i])
        else:
            combination[2] = [cards[i]]
        if len(combination[2]) == 5:
            return combination
        if len(combination[2]) == 4 and cards[i] % 13 == 0:
            if cards[i] + 12 in cards:
                combination[2].append(cards[i] + 12)
                return combination

    return None


def check_quads(cards):
    combination = ['Four Of A Kind', 7, [cards[0]]]
    for i in range(1, 7):
        if cards[i] % 13 == cards[i - 1] % 13:
            combination[2].append(cards[i])
        else:
            combination[2] = [cards[i]]
        if len(combination[2]) == 4:
            if cards[0] % 13 == combination[2][0] % 13:
                combination[2].append(cards[4])
            else:
                combination[2].append(cards[0])
            return combination

    return None


def check_boat(cards):
    combination = ['Full House', 6, []]
    best_pair = []
    temp = [cards[0]]

    for i in range(1, 7):
        if cards[i] % 13 == cards[i - 1] % 13:
            temp.append(cards[i])
        else:
            temp = []
        if len(temp) == 3:
            combination[2] += temp
            if best_pair[0] % 13 == temp[0] % 13:
                best_pair = []
            if len(best_pair) != 0:
                combination[2] += best_pair
                return combination
        elif len(temp) == 2:
            if len(combination[2]) != 0:
                combination[2] += temp
                return combination
            if len(best_pair) == 0:
                best_pair = temp
        else:
            temp = [cards[i]]
    return None


def check_flush(cards):
    combination = ['Flush', 5, [cards[0]]]
    for i in range(1, 7):
        if cards[i] // 13 == cards[i - 1] // 13:
            combination[2].append(cards[i])
        else:
            combination[2] = [cards[i]]
        if len(combination[2]) == 5:
            return combination
    return None


def check_straight(cards):
    combination = ['Straight', 4, [cards[0]]]
    for i in range(1, 7):
        if cards[i] % 13 == (cards[i - 1] - 1) % 13:
            combination[2].append(cards[i])
        elif cards[i] % 13 == cards[i - 1] % 13:
            continue
        else:
            combination[2] = [cards[i]]
        if len(combination[2]) == 5:
            return combination
        if len(combination[2]) == 4 and cards[i] % 13 == 0:
            if cards[0] % 13 == 12:
                combination[2].append(cards[0])
                return combination
    return None


def check_set(cards):
    combination = ['Three Of A Kind', 3, [cards[0]]]
    for i in range(1, 7):
        if cards[i] % 13 == cards[i - 1] % 13:
            combination[2].append(cards[i])
        else:
            combination[2] = [cards[i]]
        if len(combination[2]) == 3:
            if cards[0] % 13 == combination[2][0] % 13:
                combination[2] += [cards[3]] + [cards[4]]
            elif cards[1] % 13 == combination[2][0] % 13:
                combination[2] += [cards[0]] + [cards[4]]
            else:
                combination[2] += [cards[0]] + [cards[1]]
            return combination
    return None


def check_two(cards):
    combination = ['Two Pair', 2, []]
    temp = [cards[0]]
    for i in range(1, 7):
        if cards[i] % 13 == cards[i - 1] % 13:
            temp.append(cards[i])
            if len(temp) == 2:
                if len(combination[2]) == 0:
                    combination[2] += temp
                    temp = []
                else:
                    combination[2] += temp
                    for j in range(5):
                        if not (cards[j] in combination[2]):
                            combination[2].append(cards[j])
                            return combination
        else:
            temp = [cards[i]]

    return None


def check_pair(cards):
    combination = ['One Pair', 1, [cards[0]]]
    for i in range(1, 7):
        if cards[i] % 13 == cards[i - 1] % 13:
            combination[2].append(cards[i])
            for j in range(5):
                if cards[j] != combination[2][0] and cards[j] != combination[2][1]:
                    combination[2].append(cards[j])
                    if len(combination[2]) == 5:
                        return combination
        else:
            combination[2] = [cards[i]]
    return None
