from imagesearch import *
import pyautogui as pa
import time
from enum import Enum


FOLDER = "./image/"
MONSTER_ZONES = [
    (800, 720),
    (950, 720),
    (1100, 720)
]

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

def count_monsters(FOLDER="./image/"):
    count = 0

    for zone in MONSTER_ZONES:
        pos = imagesearcharea(
            FOLDER + "empty_monster_slot.png",
            zone[0] - 50,
            zone[1] - 50,
            zone[0] + 50,
            zone[1] + 50
        )
        # look for blank slot on board. If missing it means there is a monster there.
        if not pos or pos[0] == -1:
            count += 1

    return count


# STATES

class State(Enum):
    AT_THE_GATE = 1
    TURN_1 = 2
    DRAW_PHASE = 3
    MAIN_PHASE = 4
    END_MAIN_PHASE = 5
    BATTLE_PHASE = 6
    END_BATTLE_PHASE = 7
    WIN_SCREEN = 8
    LEVEL_SCREEN = 9
    REWARDS_SCREEN = 10
    POST_GAME = 11
    EDGE_CASE_1_REPLAY = 12
    EDGE_CASE_2_CONNECTION_DROP = 13


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
    for img in image_list:
        pos = imagesearch(folder + img)
        results[img] = pos if pos and pos[0] != -1 else None
    return results
# usage 
"""

state = get_state_images(
    ["draw.png", "victory.png", "retry.png"],
    folder
)

if state["draw.png"]:
    click_and_confirm(find_img="draw.png")


"""


def detect_state():
    for state, image in [
        (State.AT_THE_GATE, ""),
        (State.TURN_1, "turn_1.png"),
        (State.DRAW_PHASE, "draw_phase.png"),
        (State.MAIN_PHASE, "main_phase.png"),
        (State.END_MAIN_PHASE, "main_phase.png"),
        (State.BATTLE_PHASE, "battle_phase_status.png"),
        (State.END_BATTLE_PHASE, ""),
        (State.WIN_SCREEN, ""),
        (State.LEVEL_SCREEN, ""),
        (State.REWARDS_SCREEN, ""),
        (State.POST_GAME, ""),
        (State.EDGE_CASE_1_REPLAY, "replay.png"),
        (State.EDGE_CASE_2_CONNECTION_DROP, "retry.png")
    ]:
        if img(image):
            print("State:" , state.name)
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
    # Try duel button
    click_and_confirm(find_img="duel.png", timeout=10)

    # Try arrow in speech bubble
    click_and_confirm(find_img="char_arrow.png", timeout=10)

    # Try duel button
    click_and_confirm(find_img="duel.png", timeout=10)

    print("waiting...")


def handle_turn_1(): # done
    # TURN 1 IS SIGNAL TO START DRAW PHASE

    if imagesearch_loop(FOLDER+"turn_1.png", 0.1):
        print("turn1 found")   


def handle_draw_phase(): # done
    #
    # DRAW PHASE
    #
    click_and_confirm(find_img="draw_phase000.png",
                        confirm_gone_img="draw_phase000.png",
                        min_clicks=3)
                        
    click_and_confirm(find_img="card_drawn.png",
                        confirm_gone_img="card_drawn.png",
                        min_clicks=3)
               

def handle_main_phase():
    #
    # MAIN PHASE
    #

    monster_count = count_monsters()

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

                monster_count += 1
                print("Normal summon successful")
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
        
    if imagesearch(FOLDER+"battle_phase.png")[0] != -1:
        click_and_confirm(
            find_img="battle_phase.png",
            confirm_gone_img="battle_phase.png")
        print("battlephase")
    else:
        click_and_confirm(
            find_img="end_phase.png",
            confirm_gone_img="end_phase.png")
        print("endphase")


def handle_battle_phase():

    #
    # BATTLE PHASE
    #
    if monster_count >= 1:
        # Monster #1 attack
        # Find monster #1 location
        time.sleep(0.2)
        pa.click(x=1097, y=542) # should be correct
        # Find attack #1 button
        pos = imagesearch_loop(FOLDER+"attack.png", 0.1)
        print("Attack #1 button found : ", pos[0], pos[1])

        # Click attack #1 button
        if pos[0] != -1:
            click_image(FOLDER+"attack.png", pos, "left", 0.1)
        print("Attack #1 button clicked")

        # choose target when there is more than one opponent monster
        target = imagesearch(FOLDER+"target.png")
        if target[0] != -1:  
            start_time = time.time()
            timeout = 3              
            while True:
                pa.click(x=836, y=625)
                time.sleep(0.1)

                conf = imagesearch(FOLDER+"confirm.png")
                if conf[0] != -1:
                    click_image(FOLDER+"confirm.png", conf, "left", 0.1)
                    print("target confirmed")
                    break
                if time.time() - start_time > timeout:
                    print("didn't find confirmation button")
                    break        

    if monster_count >= 2:
        # Monster #2 attack
        # Find monster #2 location
        pa.click(x=1206, y=540) # should be correct
        # Find attack #2 button
        time.sleep(0.2)            
        pos = imagesearch_loop_timeout(FOLDER+"attack.png", 0.1, 0.5)
        if pos[0] != -1:
            print("Attack #2 button found : ", pos[0], pos[1])

            # Click attack #2 button
            if pos[0] != -1:
                click_image(FOLDER+"attack.png", pos, "left", 0.1)
            print("Attack #2 button clicked")
        else:
            monster_count -= 1

        # choose target when there is more than one opponent monster
        target = imagesearch(FOLDER+"target.png")
        if target[0] != -1:  
            start_time = time.time()
            timeout = 3              
            while True:
                pa.click(x=836, y=625)
                time.sleep(0.1)

                conf = imagesearch(FOLDER+"confirm.png")
                if conf[0] != -1:
                    click_image(FOLDER+"confirm.png", conf, "left", 0.1)
                    print("target confirmed")
                    break
                if time.time() - start_time > timeout:
                    print("didn't find confirmation button")
                    break 
    
def end_battle():
    #
    # END BATTLE PHASE
    #    
    pos = imagesearch_loop(FOLDER+"action.png", 0.1)
    print("Action button found : ", pos[0], pos[1])

    # Click action button
    if pos[0] != -1:
        click_image(FOLDER+"action.png", pos, "left", 0.1)
    print("Action button clicked")

    # Find end phase button
    pos = imagesearch_loop(FOLDER+"end_phase.png", 0.1)
    print("End phase button found : ", pos[0], pos[1])

    # Click end phase button
    if pos[0] != -1:
        click_image(FOLDER+"end_phase.png", pos, "left", 0.1)
    print("End phase button clicked")


def handle_win_screen():
    #
    # AFTER DUEL
    #
    # WIN SCREEN
    click_and_confirm(find_img="ok.png", min_clicks=3)
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
    if end_game(FOLDER+"max_level.png", 1):
        finished = True
        #break

    # Click next button
    if pos[0] != -1:
        click_image(FOLDER+"next.png", pos, "left", 0.5)
    print("Next button clicked")


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

def handle_post_duel():
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

while True:
    emergency_checks()

    new_state = detect_state()
    if new_state != state:
        print("State: ", new_state)
        state = new_state

    if state == State.AT_THE_GATE:
        handle_gate()

    elif state == state.TURN_1:
        handle_turn_1()

    elif state == State.DRAW_PHASE:
        handle_draw_phase()

    elif state == State.MAIN_PHASE:
        handle_main_phase()

    elif state == state.END_MAIN_PHASE:
        end_main_phase()

    elif state == State.BATTLE_PHASE:
        handle_battle_phase()

    elif state == state.END_BATTLE_PHASE:
        end_battle()

    elif state == State.WIN_SCREEN:
        handle_win_screen()

    elif state == State.LEVEL_SCREEN:
        handle_level_screen()

    elif state == State.REWARDS_SCREEN:
        handle_rewards_screen()

    elif state == state.POST_GAME:
        handle_post_duel()

    elif state == State.EDGE_CASE_1_REPLAY:
        handle_replay()

    elif state == State.EDGE_CASE_2_CONNECTION_DROP:
        connection_drop()

    time.sleep(0.1)








### EVERYTHING BELOW HERE IS A SUGGESTION FOR LATER ###

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


    

### THESE ARE SOME FUNCTIONS TO INCORPORATE LATER ###




# back off and retry logic
def wait_for_image(img, timeout=3, folder="./images/"):
    start = time.time()
    delay = 0.05

    while time.time() - start < timeout:
        pos = imagesearch(folder + img)
        if pos and pos[0] != -1:
            return pos

        time.sleep(delay)
        delay = min(delay * 1.5, 0.5)  # cap at 0.5s

    return None

"""
Why This Is Better:

Checks quickly at first

Slows down gradually

Reduces CPU usage

Looks more human

Improves stability

"""


"""
What I Recommend For Your Duel Links Bot

Best setup:

Cached state scan per frame

Separate click + confirm functions

Backoff waiting

Single responsibility functions

Avoid repeated image searches


That combination will:

Improve reliability

Reduce CPU usage

Reduce desync bugs

Make debugging easier
"""  


    

 

    

    




