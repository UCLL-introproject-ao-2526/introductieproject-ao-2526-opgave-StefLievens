import copy
import random
import pygame


pygame.init()

#game variables
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# [dn] dit ziet er cool uit, maar is wel zeer irritant om te typen (je gaat het moeten copy pasten)
# [dn] ['C', 'D', 'S', 'H'] is minder cool, maar wel handiger
suits = ['♥', '♦', '♣', '♠']


one_deck = [[v, s] for v in values for s in suits]

# [dn] naming can wel beter. Dit is geen deck, maar het aantal decks. bvb amount_of_decks
decks = 4 

WIDTH = 850
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Blackjack!')
fps = 60
timer = pygame.time.Clock()


font = pygame.font.SysFont('arial', 44, bold=True)
smaller_font = pygame.font.SysFont('arial', 36, bold=True)
active = False

#win, loss, draw
records = [0, 0, 0]
player_score = 0
split_score = 0
dealer_score = 0
initial_deal = False
my_hand = []
split_hand = []
is_split = False
# [dn] hier weet ik ook niet wat active_hand echt betekent van de naam
active_hand = 1
dealer_hand = []
outcome = 0
split_outcome = 0
reveal_dealer = False
hand_active = False
outcome = 0
add_score = False
results = [' ', 'PLAYER BUSTED o_O', 'PLAYER WINS!', 'DEALER WINS!', 'TIE GAME...']


#deal cards by selecting randomly from deck, and make function for one card at a time
# [dn] maar 1 kaart maar de functie heet deal_cards?
def deal_cards(current_hand, current_deck):
    card = random.randrange(0, len(current_deck))
    current_hand.append(current_deck[card])
    current_deck.pop(card)
    return current_hand, current_deck


#draw scores for player, split hand and dealer on screen
def draw_scores(player, dealer, split, splitted):
    if not splitted:
        screen.blit(font.render(f'Score[{player}]', True, 'white'), (550, 480))
    else:
        player_text = f'Score1[{player}]' + (' *' if active_hand == 1 and hand_active else '')
        split_text = f'Score2[{split}]' + (' *' if active_hand == 2 and hand_active else '')
        screen.blit(font.render(player_text, True, 'white'), (550, 480))
        screen.blit(font.render(split_text, True, 'white'), (550, 550))

    if reveal_dealer:
        screen.blit(font.render(f'Score[{dealer}]', True, 'white'), (550, 180))


#draw cards visually onto screen
def draw_cards(player, dealer, reveal, split, splitted):
    #function to draw individual cards
    def draw_single_card(card, x, y, is_dealer_hidden=False):
        pygame.draw.rect(screen, 'white', [x, y, 120, 220], 0, 5)

        if is_dealer_hidden:
            screen.blit(font.render('???', True, 'black'), (x + 15, y + 15))
            pygame.draw.rect(screen, 'blue', [x, y, 120, 220], 5, 5)
            return
        
        #decide color on symbol
        card_value, card_suit = card[0], card[1]
        text_color = 'red' if card_suit in ['♥', '♦'] else 'black'

        #draw symbol and value
        val_text = font.render(card_value, True, text_color)
        suit_text = font.render(card_suit, True, text_color)
        screen.blit(val_text, (x + 8, y + 5))
        screen.blit(suit_text, (x + 8, y + 45))

        #draw symbol in the middle of the card
        large_font = pygame.font.SysFont('arial', 72, bold=True)
        center_suit = large_font.render(card_suit, True, text_color)
        screen.blit(center_suit, (x + 38, y + 80))



    #hand 1 shown more to the left if split
    x_offset = 40 if splitted else 70
    for i in range(len(player)):
        x_pos = x_offset + (50 * i)
        y_pos = 460 + (5 * i)
        draw_single_card(player[i], x_pos, y_pos)

        border_color = 'gold' if (active_hand == 1 and splitted and hand_active) else 'red'
        pygame.draw.rect(screen, border_color, [x_pos, y_pos, 120, 220], 5, 5)


    #hand 2 shown more to the right
    if splitted:
        for i in range(len(split)):
            x_pos = 300 + (50 * i)
            y_pos = 460 + (5 * i)
            draw_single_card(split[i], x_pos, y_pos)

            border_color = 'gold' if (active_hand == 2 and splitted and hand_active) else 'red'
            pygame.draw.rect(screen, border_color, [x_pos, y_pos, 120, 220], 5, 5)
    
    #if player hasn't finished turn, dealer will hide one card
    for i in range(len(dealer)):
        x_pos = 70 + (70 * i)
        y_pos = 160 + (5 * i)
        hidden = (i == 0 and not reveal)

        draw_single_card(dealer[i], x_pos, y_pos, is_dealer_hidden=hidden)

        if not hidden:
            pygame.draw.rect(screen, 'blue', [x_pos, y_pos, 120, 220], 5, 5)



# pass in player or dealer hand and get best score possible
def calculate_score(hand):
    #calculate hand score fresh every time, checkk how many aces we have
    hand_score = 0
    aces_count = 0

    for card in hand:
        card_value = card[0]
        if card_value.isdigit():
            hand_score += int(card_value)
        elif card_value in ['10', 'J', 'Q', 'K']:
            hand_score += 10
        elif card_value == 'A':
            hand_score += 11
            aces_count +=1

    while hand_score > 21 and aces_count > 0:
        hand_score -= 10
        aces_count -=1
        
    return hand_score


#draw game condition and buttons
def draw_game(act, record, result, split_result, can_split, splitted):
    button_list = []
    #init on startup (not active) only option is to deal new hand
    if not act:
        deal = pygame.draw.rect(screen, 'white', [275,20,300,100], 0, 5)
        pygame.draw.rect(screen, 'gold', [275,20,300,100], 3, 5)
        deal_text = font.render('DEAL HAND', True, 'black')
        screen.blit(deal_text, (298,50))
        button_list.append(deal)

    #once game started, show hit and stand buttons and win/loss records
    else:
        #hit
        hit = pygame.draw.rect(screen, 'white', [25, 750, 400, 100], 0, 5)
        pygame.draw.rect(screen, 'gold', [25, 750, 400,100], 3, 5)
        hit_text = font.render('HIT ME', True, 'black')
        screen.blit(hit_text, (140,780))
        button_list.append(hit)

        #stand
        stand = pygame.draw.rect(screen, 'white', [425, 750,400,100], 0, 5)
        pygame.draw.rect(screen, 'gold', [425, 750,400,100], 3, 5)
        stand_text = font.render('STAND', True, 'black')
        screen.blit(stand_text, (550,780))
        button_list.append(stand)

        #scoreboard
        score_text = smaller_font.render(f'Wins: {record[0]}    Losses: {record[1]}    Draws: {record[2]}', True, 'white')
        screen.blit(score_text, (155, 880))

        #split only when possible
        if can_split and not splitted:
            split = pygame.draw.rect(screen, 'white', [550, 380, 200, 60], 0, 5)
            pygame.draw.rect(screen, 'gold', [550, 380, 200, 60], 3, 5)
            screen.blit(smaller_font.render('SPLIT', True, 'black'), (595, 392))
            button_list.append(split)
        else:
            button_list.append(pygame.Rect(0, 0 , 0, 0))
    
    #results
    if result != 0:
        result_text = results[result] if not splitted else f'Hand 1: {results[result]}'
        screen.blit(font.render(result_text, True, 'white'), (15, 25))
    if split_result != 0 and splitted:
        screen.blit(font.render(f'Hand 2: {results[split_result]}', True, 'white'), (15, 80))

    #new hand
    if result != 0 and (not splitted or split_result != 0):
        deal = pygame.draw.rect(screen, 'white', [275,220,300,100], 0, 5)
        pygame.draw.rect(screen, 'gold', [275,220,300,100], 3, 5)
        pygame.draw.rect(screen, 'black', [278,223,294,94], 3, 5)
        deal_text = font.render('NEW HAND', True, 'black')
        screen.blit(deal_text, (305,250))
        button_list.append(deal)

    return button_list


#check endgame conditions function
def check_endgame(hand_act, deal_score, play_score, result, totals, add):
    #check end game scenarion if player has stood, busted of blackjacked
    #result 1- player bust, 2- win, 3- loss, 4- draw
    if not hand_act and deal_score >=17:
        if play_score > 21:
            result = 1
        elif deal_score < play_score <= 21 or deal_score > 21:
            result = 2
        elif play_score < deal_score <= 21:
            result = 3
        else:
            result = 4
        if add:
            if result == 1 or result ==3:
                totals[1] += 1
            elif result == 2:
                totals[0] += 1
            else:
                totals[2] +=1
            add = False
    return result, totals, add


#main game loop
run = True
while run:
    #run game at framerate and fill screen with bg color
    timer.tick(fps)
    screen.fill((20, 110, 55))

    #initial deal to player and dealer
    if initial_deal:
        for i in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        initial_deal = False

    #once game is actived, and dealt, calculate scores and display cards
    if active:
        player_score = calculate_score(my_hand)
        if is_split:
            split_score = calculate_score(split_hand)
        
        draw_cards(my_hand, dealer_hand, reveal_dealer, split_hand, is_split)
        
        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)
            if dealer_score < 17 and not hand_active:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
                dealer_score = calculate_score(dealer_hand)

        draw_scores(player_score, dealer_score, split_score, is_split)

    #is split possible?
    can_split = False
    if len(my_hand) == 2 and active:
        val1 = 10 if my_hand[0][0] in ['J','Q','K','10'] else my_hand[0][0]
        val2 = 10 if my_hand[1][0] in ['J','Q','K','10'] else my_hand[1][0]
        if val1 == val2:
            can_split = True

    buttons = draw_game(active, records, outcome, split_outcome, can_split, is_split)

    #event handling, if quit pressed, then exit game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONUP:
            if not active:
                if buttons[0].collidepoint(event.pos):
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck)
                    my_hand, split_hand = [], []
                    dealer_hand = []
                    outcome, split_outcome = 0, 0
                    hand_active = True
                    reveal_dealer = False
                    is_split = False
                    active_hand = 1
                    add_score = True
                    dealer_score, player_score, split_score = 0, 0, 0

            # [dn] je zit nu zo diep in je if/else/elif dat het onduidelijk is welke else we heire hebben
            else: 
                #if player can hit, allow them to draw a card
                if buttons[0].collidepoint(event.pos) and hand_active:
                    if active_hand == 1 and player_score < 21:
                        my_hand, game_deck = deal_cards(my_hand, game_deck)
                    elif active_hand == 2 and split_score < 21:
                        split_hand, game_deck = deal_cards(split_hand, game_deck)

                #allow play to end turn(stand)
                elif hand_active and buttons[1].collidepoint(event.pos) and not reveal_dealer:
                    if is_split and active_hand == 1:
                        active_hand = 2
                    else:
                        reveal_dealer = True
                        hand_active = False

                #split button has been hit
                elif can_split and not is_split and buttons[2].collidepoint(event.pos):
                    is_split = True
                    split_hand.append(my_hand.pop())
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                    split_hand, game_deck = deal_cards(split_hand, game_deck)

                #new hand
                elif (outcome != 0 and (not is_split or split_outcome != 0)) and buttons[-1].collidepoint(event.pos):
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck)
                    my_hand, split_hand = [], []
                    dealer_hand = []
                    outcome, split_outcome = 0, 0
                    hand_active = True
                    reveal_dealer = False
                    is_split = False
                    active_hand = 1
                    add_score = True
                    dealer_score, player_score, split_score = 0, 0, 0
                    

    #if player busts, automatically end turn (stand)
    if hand_active:
        if active_hand == 1 and player_score >=21:
            if is_split:
                active_hand = 2
            else:
                hand_active = False
                reveal_dealer = True
        elif active_hand == 2 and split_score >= 21:
            hand_active = False
            reveal_dealer = True

    #calculate score
    if not hand_active and reveal_dealer and dealer_score >= 17:
        if add_score:
            outcome, records, _ = check_endgame(hand_active, dealer_score, player_score, outcome, records, True)
            if is_split:
                split_outcome, records, _  = check_endgame(hand_active, dealer_score, split_score, split_outcome, records, True)
        add_score = False

    pygame.display.flip()
pygame.quit()
