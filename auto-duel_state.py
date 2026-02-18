from imagesearch import *
import pyautogui as pa
import time
from enum import Enum


FOLDER = "./image/"
BLANK = ["blank1.png", "blank2.png", "blank3.png"]

GAME_STATE = {
    "monster_count": 0,
}

"""def poke_screen(duration=1):
    start = time.time()
    while time.time() - start < duration:
        pa.click(960, 832)
        time.sleep(0.3)"""


    
"""Use multiple confirmation images (huge improvement)

Don’t trust a single PNG.

For example, Gate screen:

GATE_SIGNS = [
    "gate.png",
    "standard_duelist.png",
    "gate_background.png"
]

def at_gate():
    return any(imagesearch(folder+img)[0] > -1 for img in GATE_SIGNS)
"""

def stable_imagesearch(image_path, checks=3, delay=0.1):
    for _ in range(checks):
        pos = imagesearch(image_path)
        if not pos or pos[0] == -1:
            return None
        time.sleep(delay)
    return pos


def click_target(
    deadline,
    find_img=None,
    coords=None,    
    click_delay=0.3,
    img_folder=FOLDER
):
    
    if not find_img and not coords:
        raise ValueError("Either find_img or coords must be provided")
     
    pos = None

    # Click phase
    while time.time() < deadline:
        if coords:
            pos = coords
        else:
            # confirm stable target
            pos = stable_imagesearch(img_folder + find_img)
        
        if coords or ( pos and pos[0] != -1):
            break

    if not pos:
        return False # target not found

    # click once
    x, y = pos
    pa.click(x, y)

    target = coords if coords else find_img
    print(f"Clicking: {target}")
    
    time.sleep(click_delay)

    return True

def confirm_state(
    deadline,
    confirm_gone_img=None,
    confirm_appear_img=None, 
    folder=FOLDER
):
    
    if not confirm_gone_img and not confirm_appear_img:
        return True
    
    # Confirmation phase
    while time.time()  < deadline:

        if confirm_appear_img:
            # use stable image search for appear img
            pos = stable_imagesearch(folder + confirm_appear_img)
            if pos and pos[0] != -1:
                print(f"Confirmed appearance: {confirm_appear_img}")
                return True        
    
        if confirm_gone_img:
            # use stable image search here as well
            pos = stable_imagesearch(folder + confirm_gone_img)
            if not pos or pos[0] == -1:
                print(f"Confirmed disappearance: {confirm_gone_img}")
                return True    

        time.sleep(0.1)
    print("Timeout waiting for confirmation")

    return False

def click_and_confirm(
    find_img=None,
    coords=None,
    confirm_gone_img=None,
    confirm_appear_img=None,    
    timeout=2,
    click_delay=0.3,
    img_folder=FOLDER):

    deadline = time.time() + timeout

    if click_target(
        deadline=deadline,
        find_img=find_img,
        coords=coords,    
        click_delay=click_delay,
        img_folder=img_folder):

        return confirm_state(
            deadline=deadline,
            confirm_gone_img=confirm_gone_img,
            confirm_appear_img=confirm_appear_img, 
            folder=img_folder)
    
    return False

"""
# back off and retry logic
#Checks quickly at first. Slows down gradually. Reduces CPU usage
def wait_for_image(img, timeout=3, folder=FOLDER):
    start = time.time()
    delay = 0.05

    while time.time() - start < timeout:
        pos = imagesearch(folder + img)
        if pos and pos[0] != -1:
            return pos

        time.sleep(delay)
        delay = min(delay * 1.5, 0.5)  # cap at 0.5s

    return None"""

def end_game(img, timeout=1): # merge this with handle_end_game function
    start = time.time()

    while time.time() - start < timeout:
        if imagesearch(img, 0.9)[0] > -1:
            print("max level reached")
            return True
    return False

def replay_click(message_img, yes_img, timeout=1): # merge this with handle_replay function
    start = time.time()

    while time.time() - start < timeout:
        if imagesearch(message_img)[0] > -1:
            print("replay happens")
            return click_and_confirm(yes_img, 
                                   confirm_gone_img=message_img 
                                   )
        time.sleep(0.1)
    return False


def count_monsters(blank_images, folder=FOLDER):
    blank_count = 0

    for img in blank_images:
        pos = imagesearch(folder + img)
        if pos[0] != -1:  # found blank space
            blank_count += 1

    # Monster count = total zones (3) - blank_count
    monster_count = 3 - blank_count
    return monster_count



# STATES

class State(Enum):
    AT_THE_GATE = 1
    DRAW_PHASE = 2
    MAIN_PHASE = 3
    BATTLE_PHASE = 4
    WIN_SCREEN = 5
    LEVEL_SCREEN = 6
    REWARDS_SCREEN = 7
    CHAR_SPEECH = 8
    EDGE_CASE_1_REPLAY = 9
    EDGE_CASE_2_CONNECTION_DROP = 10


def img(name, confidence=0.8, timeout=1, interval=0.1):

    """
    name       → image file name
    confidence → image match precision
    timeout    → how long to keep retrying (seconds)
    interval   → delay between retries
    """
    path = FOLDER + name
    start = time.time()

    while True:
        pos = imagesearch(path, confidence)
        if pos[0] != -1:
            return pos  # found
        if timeout == 0:
            return None  # single attempt only
        if time.time() - start > timeout:
            return None  # gave up

        time.sleep(interval)

# caching images
def get_state_images(image_list, folder=FOLDER):
    results = {}
    for state, img in image_list:
        pos = imagesearch(folder + img, 0.9)
        results[state] = pos if pos and pos[0] != -1 else None
    return results


STATE_IMAGE_MAP =  [
        (State.AT_THE_GATE, "at_gate.png"),
        (State.DRAW_PHASE, "draw_phase.png"),
        (State.MAIN_PHASE, "main_phase.png"),
        (State.BATTLE_PHASE, "battle_phase_status.png"),
        (State.WIN_SCREEN, "win1.png"),
        (State.LEVEL_SCREEN, "level_screen.png"),
        (State.REWARDS_SCREEN, "rewards_screen.png"),
        (State.CHAR_SPEECH, "char_arrow.png"), 
        (State.EDGE_CASE_1_REPLAY, "replay.png"),
        (State.EDGE_CASE_2_CONNECTION_DROP, "retry.png")
    ]


def detect_state(screen_state):
    for state, pos in screen_state.items():   # <-- use .items() for dict
        if pos:  # pos is not None, image was found
            print("Detected state:", state)
            return state
    return None




def emergency_checks():
    if img("disconnect.png"):
        sys.exit("Disconnected")

    if img("maintenance.png"):
        sys.exit("Maintenance")


def handle_gate(): # done
    #
    # AT THE GATE
    #

    no_keys = stable_imagesearch(FOLDER+"no_keys.png")
    if no_keys:
        return True
    # Try duel button
    click_and_confirm(find_img="duel.png", timeout=10)

    click_and_confirm(find_img="char_arrow.png", timeout=10)

    click_and_confirm(find_img="duel.png", timeout=10)

    return False


def handle_draw_phase(): # done
    #
    # DRAW PHASE
    #
    click_and_confirm(find_img="draw_phase000.png",
                        confirm_gone_img="draw_phase000.png",
                        timeout=5)
                        
    click_and_confirm(find_img="card_drawn.png",
                        confirm_gone_img="card_drawn.png", timeout=5)
    
    time.sleep(0.5)
               

def handle_main_phase():
    #
    # MAIN PHASE
    #

    monster_count = count_monsters(BLANK)

    if monster_count < 2:
        print("Attempting summon...")

        if click_and_confirm(coords=(1056, 850), 
                                confirm_appear_img="normal_summon.png",
                                timeout=5):
            print("Clicked summon menu coordinates")

            if click_and_confirm(find_img="normal_summon.png",
                                        confirm_gone_img="normal_summon.png",
                                        timeout=5):
                print("normal summoned")

            else:
                print("Failed to find normal summon button")  
    return monster_count


def end_main_phase():
    # Find and click action button.                  

    if click_and_confirm(find_img="action.png",
                            confirm_appear_img="end_phase.png",
                            timeout=5):
        print("action button clicked")
    else:
        print("action button not found.")

    # Find battle phase button or end phase if turn 1

    is_turn1 = stable_imagesearch(FOLDER+"turn_1.png")      
        
    if is_turn1:
        print("Turn 1 detected → skipping battle phase")
        click_and_confirm(
            find_img="end_phase.png",
            confirm_gone_img="end_phase.png")
        print("endphase")

    else: 
        click_and_confirm(
            find_img="battle_phase.png",
            confirm_gone_img="battle_phase.png")
        print("battlephase")

def full_main_phase():
    GAME_STATE["monster_count"] = handle_main_phase()
    end_main_phase()


def attack_monster(index):
    """
    Click a monster and attack if the attack button appears.
    Handles fast-disappearing attack buttons with a short retry window.
    """
    monster_positions = [
        (1097, 542),
        (1206, 540)
    ]

    if index >= len(monster_positions):
        return False

    x, y = monster_positions[index]
    pa.click(x=x, y=y)
    print(f"Clicked monster {index}")

    # Wait up to 700ms for the attack button to appear
    start_time = time.time()
    pos = None
    while time.time() - start_time < 0.7:
        pos = stable_imagesearch(FOLDER + "attack.png")
        if pos and pos[0] != -1:
            break        
        time.sleep(0.05)

    if not pos or pos[0] == -1:
        print(f"Attack button not found for monster {index} — skipping")
        return False

    if click_image(FOLDER + "attack.png", pos, "left", 0.05):
        print(f"Attack button clicked for monster {index}")

    choose_target()
    return True


def choose_target():
    target = imagesearch(FOLDER+"target.png")
    if target[0] != -1:
        start_time = time.time()
        timeout = 3
        while True:
            pa.click(x=836, y=625)
            time.sleep(1)

            conf = stable_imagesearch(FOLDER+"confirm.png")
            if conf[0] != -1:
                if click_and_confirm(find_img="confirm.png", 
                                     confirm_gone_img="confirm.png", 
                                     ):
                    print("target confirmed")
                    break

            if time.time() - start_time > timeout:
                print("didn't find confirmation button")
                break


def handle_battle_phase():

    #
    # BATTLE PHASE
    #
    monster_count = count_monsters(BLANK)
    print(f"Monsters detected: {monster_count}")

    if monster_count >= 3:
        choose_target() # if confirm screen is covering monsters


    for i in range(monster_count):
        success = attack_monster(i)
        time.sleep(3) # will miss the timing of second monster without this
        if not success:
            print(f"Monster {i} : Attack failed or skipped")
        else:
            print(f"Monster {i} attack succeeded")
    

def end_battle():
    #
    # END BATTLE PHASE
    #    
    pos = imagesearch_loop_timeout(FOLDER+"action.png", 0.1, 5)
    print("Action button found : ", pos[0], pos[1])

    # Click action button
    if pos[0] != -1:
        click_image(FOLDER+"action.png", pos, "left", 0.1)
    print("Action button clicked")

    # Find end phase button
    pos = imagesearch_loop_timeout(FOLDER+"end_phase.png", 0.1, 5)
    print("End phase button found : ", pos[0], pos[1])

    # Click end phase button
    if pos[0] != -1:
        click_image(FOLDER+"end_phase.png", pos, "left", 0.1)
    print("End phase button clicked")


def full_battle_phase():
    handle_battle_phase()
    end_battle()


def handle_win_screen():
    #
    # AFTER DUEL
    #
    # WIN SCREEN
    click_and_confirm(find_img="ok.png")
    print("OK button clicked")


def handle_level_screen():
    #
    # LEVEL SCREEN
    #
    # Wait next button
    search = True
    while search:
        pos = imagesearch(FOLDER+"next.png")
        if pos[0] != -1:
            search = False
        for _ in range(3):
            pa.click(x=960, y=832)
        time.sleep(0.3)
    print("Next button found")

    # check if max level reached
    for pic in ["max_level35.png", "max_level40.png"]:
        if end_game(FOLDER + pic, 1):
            return True       

    # Click next button
    if pos[0] != -1:
        click_image(FOLDER+"next.png", pos, "left", 0.5)
    print("Next button clicked")

    return False


def handle_rewards_screen():
    # REWARDS SCREEN

    # Wait next button
    search = True
    while search:
        pos = imagesearch(FOLDER+"next.png")
        if pos[0] != -1:
            search = False
        for _ in range(3):
            pa.click(x=960, y=832)
        time.sleep(0.3)
    print("Next button found")

    # Click next button
    if pos[0] != -1:
        click_image(FOLDER+"next.png", pos, "left", 0.5)
    print("Next button clicked")

def handle_char_speech():
    #
    # POST GAME
    #
    # Try character
    click_and_confirm(find_img="char_arrow.png", timeout=10)

def handle_replay():
    #
    # EDGE CASE IF REPLAY IS NEEDED IN BATTLE
    # 
    # check for replay
    if replay_click(FOLDER+"replay.png", FOLDER+"yes.png", 1):
        time.sleep(3)
    pos = imagesearch(FOLDER+"battle_phase_status.png")
    if pos[0] == -1:
        pass # fix this later 

def connection_drop():
    #
    # EDGE CASE IF CONNECTION DROPS
    #
    # click retry if connection breaks
    click_and_confirm(find_img="retry.png")


# Main loop

state = None

turn1_seen = False

while True:
    #emergency_checks()

    screen_state = get_state_images(STATE_IMAGE_MAP)
    state = detect_state(screen_state)


    if state == State.AT_THE_GATE:
        if handle_gate():
            print("Exiting: No keys left")
            break

    elif state == State.DRAW_PHASE:
        handle_draw_phase()

    elif state == State.MAIN_PHASE:
        full_main_phase()

    elif state == State.BATTLE_PHASE:
        full_battle_phase()

    elif state == State.WIN_SCREEN:
        handle_win_screen()

    elif state == State.LEVEL_SCREEN:
        if handle_level_screen():
            print("Exiting: Max Level reached")
            break

    elif state == State.REWARDS_SCREEN:
        handle_rewards_screen()

    elif state == State.CHAR_SPEECH:
        handle_char_speech()

    elif state == State.EDGE_CASE_1_REPLAY:
        handle_replay()

    elif state == State.EDGE_CASE_2_CONNECTION_DROP:
        connection_drop()

    time.sleep(0.1)


