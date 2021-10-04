RANKS = '34567890JQKA2'
SUITS = 'DCHS'

def get_card_score(card):
  rank_score = RANKS.index(card[0])
  suit_score = SUITS.index(card[1])
  return (rank_score, suit_score)

def compare_singles(card1, card2):
  return get_card_score(card1) > get_card_score(card2)

def compare_pair(pair1, pair2):
  pair1_rank = RANKS.index(pair1[0][0])
  pair2_rank = RANKS.index(pair2[0][0])
  if pair1_rank == pair2_rank:
    return 'S' in (pair1[0][1], pair1[1][1])
  return pair1_rank > pair2_rank

def compare_triple(triple1, triple2):
  triple1_rank = RANKS.index(triple1[0][0])
  triple2_rank = RANKS.index(triple2[0][0])
  return triple1_rank > triple2_rank
 
def identify_play(cards):
  if len(cards) != 5:
    return 'invalid play'
  
  cards.sort(key=get_card_score)
  # Check straight flush, straight, and flush
  # If the sorted ranks are in CARD_RANKS that means they're sequential
  straight = ''.join([x[0] for x in cards]) in RANKS
  # If there's only one suit, it is a flush.
  flush = len({x[1] for x in cards}) == 1
  
  if straight and flush:
    return 'straight flush'
  elif flush:
    return 'flush'
  elif straight:
    return 'straight'
  
  # Check full house and four of a kind
  rank_counts = {}
  # Tally how many of each rank occurs
  for card in cards:
    rank_counts[card[0]] = rank_counts.get(card[0], 0) + 1
  if len(rank_counts) == 2:
    # If there's only two ranks it has to be a full house of four of a kind
    if 4 in rank_counts.values():
      return 'four of a kind'
    return 'full house'
  
  return 'invalid play'

def is_better_play(first, second):
  if len(first) != len(second):
    return False
  
  if len(first) == 1:
    return compare_singles(first[0], second[0])
  
  elif len(first) == 2:
    return compare_pair(first, second)
  
  elif len(first) == 3:
    return compare_triple(first, second)
  
  elif len(first) == 5:
    type_ranks = ['straight', 'flush', 'full house', 'four of a kind', 'straight flush']
    
    first.sort(key=get_card_score)
    second.sort(key=get_card_score)

    first_type = identify_play(first)
    second_type = identify_play(second)
    
    if first_type != second_type:
      return type_ranks.index(first_type) > type_ranks.index(second_type)
    
    if first_type == 'straight' or first_type == 'straight flush':
      return get_card_score(first[-1]) > get_card_score(second[-1])
    
    if first_type == 'flush':
      first_suit = first[0][1]
      second_suit = second[0][1]
      
      if first_suit != second_suit:
        return SUITS.index(first_suit) > SUITS.index(second_suit)
      return get_card_score(first[-1]) > get_card_score(second[-1])
    
    if first_type == 'full house' or first_type == 'four of a kind':
      return get_card_score(first[2]) > get_card_score(second[2])

def is_pair(card1, card2):
  # TODO implement this function
  if card1[0] == card2[0]:
    return True
  return False

def is_triple(card1, card2, card3):
  if card1[0] == card2[0] == card3[0]:
    return True
  return False

def is_quad(card1, card2, card3, card4):
  if card1[0] == card2[0] == card3[0] == card4[0]:
    return True
  return False

def valid_play(cards):
    if len(cards) == 1:
        return True
    elif len(cards) == 2:
        return is_pair(cards[0], cards[1])
    elif len(cards) == 3:
        return is_triple(cards[0], cards[1], cards[2])
    elif len(cards) == 4:
        return is_quad(cards[0], cards[1], cards[2], cards[3])
    elif len(cards) == 5:
        if identify_play(cards) == 'invalid play':
            return False
        return True
    else:
        return False