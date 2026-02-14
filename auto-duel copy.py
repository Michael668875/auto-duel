from imagesearch import *
import pyautogui as pa
import time
from enum import Enum


folder = "./image/" # remove this when find_and_click function is phased out
character = "arrow"
IMAGE_FOLDER = "./image/" # for click_and_confirm function
MONSTER_ZONES = [
    (800, 720),
    (950, 720),
    (1100, 720)
]


def find_and_click(image_path, timeout=1, click_delay=0.5): # phase this out and replace with click_and_confirm function
    start = time.time()

    while time.time() - start < timeout:
        pos = imagesearch(image_path)
        if pos[0] != -1:
            print(f"Found {image_path} at", pos)
            click_image(image_path, pos, "left", click_delay)
            return True
        
        time.sleep(0.1) # small pause to avoid CPU abuse

    print(f"{image_path} not found within {timeout}s")
    return False

def click_and_confirm(
    find_img=None,
    coords=None,
    confirm_gone_img=None,
    confirm_appear_img=None,
    timeout=2,
    click_delay=0.3,
    min_clicks=1,
    folder=IMAGE_FOLDER
):
    
    if not find_img and not coords:
        raise ValueError("Either find_img or coords must be provided")
     
    start = time.time()
    clicks = 0

    # Click phase
    while clicks < min_clicks and time.time() - start < timeout:
        if coords:
            pos = coords
        else:
            pos = imagesearch(folder + find_img)
        
        if coords or ( pos and pos[0] != -1):
            x, y = pos if coords else pos

            target = coords if coords else find_img
            print(f"Clicking: {target}")
            
            pa.click(x, y)
            clicks += 1
            time.sleep(click_delay)

        else:
            time.sleep(0.1)

    # Confirmation phase
    confirm_start = time.time()
    while time.time() - confirm_start < timeout:

        if confirm_appear_img:
            pos = imagesearch(folder + confirm_appear_img)
            if pos and pos[0] != -1:
                print(f"Confirmed appearance: {confirm_appear_img}")
                return True
        
    
        if confirm_gone_img:
            pos = imagesearch(folder + confirm_gone_img)
            if not pos or pos[0] == -1:
                print(f"Confirmed disappearance: {confirm_gone_img}")
                return True    

        time.sleep(0.1)
    target = find_img if find_img else f"coords {coords}"
    print(f"timeout waiting for {target}")

    return False


"""def click_until_next(current_img, next_img, click_pos, timeout=3):
    start = time.time()

    while time.time() - start < timeout:
        if imagesearch(next_img)[0] > -1:
            return True
        
        if imagesearch(current_img)[0] > -1:
            pa.click(*click_pos)

        time.sleep(0.1)

    return False"""

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

def count_monsters(folder="./image/"):
    count = 0

    for zone in MONSTER_ZONES:
        pos = imagesearcharea(
            folder + "empty_monster_slot.png",
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
    path = folder + name
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

    if imagesearch_loop(folder+"turn_1.png", 0.1):
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
        
    if imagesearch(folder+"battle_phase.png")[0] != -1:
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
        pos = imagesearch_loop(folder+"attack.png", 0.1)
        print("Attack #1 button found : ", pos[0], pos[1])

        # Click attack #1 button
        if pos[0] != -1:
            click_image(folder+"attack.png", pos, "left", 0.1)
        print("Attack #1 button clicked")

        # choose target when there is more than one opponent monster
        target = imagesearch(folder+"target.png")
        if target[0] != -1:  
            start_time = time.time()
            timeout = 3              
            while True:
                pa.click(x=836, y=625)
                time.sleep(0.1)

                conf = imagesearch(folder+"confirm.png")
                if conf[0] != -1:
                    click_image(folder+"confirm.png", conf, "left", 0.1)
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
        pos = imagesearch_loop_timeout(folder+"attack.png", 0.1, 0.5)
        if pos[0] != -1:
            print("Attack #2 button found : ", pos[0], pos[1])

            # Click attack #2 button
            if pos[0] != -1:
                click_image(folder+"attack.png", pos, "left", 0.1)
            print("Attack #2 button clicked")
        else:
            monster_count -= 1

        # choose target when there is more than one opponent monster
        target = imagesearch(folder+"target.png")
        if target[0] != -1:  
            start_time = time.time()
            timeout = 3              
            while True:
                pa.click(x=836, y=625)
                time.sleep(0.1)

                conf = imagesearch(folder+"confirm.png")
                if conf[0] != -1:
                    click_image(folder+"confirm.png", conf, "left", 0.1)
                    print("target confirmed")
                    break
                if time.time() - start_time > timeout:
                    print("didn't find confirmation button")
                    break 
    
def end_battle():
    #
    # END BATTLE PHASE
    #    
    pos = imagesearch_loop(folder+"action.png", 0.1)
    print("Action button found : ", pos[0], pos[1])

    # Click action button
    if pos[0] != -1:
        click_image(folder+"action.png", pos, "left", 0.1)
    print("Action button clicked")

    # Find end phase button
    pos = imagesearch_loop(folder+"end_phase.png", 0.1)
    print("End phase button found : ", pos[0], pos[1])

    # Click end phase button
    if pos[0] != -1:
        click_image(folder+"end_phase.png", pos, "left", 0.1)
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
        pos = imagesearch(folder+"next.png")
        if pos[0] != -1:
            search = False
        for _ in range(3):
            pa.click(x=960, y=832)
        time.sleep(0.3)
    print("Next button found")

    # check if max level reached
    if end_game(folder+"max_level.png", 1):
        finished = True
        #break

    # Click next button
    if pos[0] != -1:
        click_image(folder+"next.png", pos, "left", 0.5)
    print("Next button clicked")


def handle_rewards_screen():
    # REWARDS SCREEN

    # Wait next button
    search = True
    while search:
        pos = imagesearch(folder+"next.png")
        if pos[0] != -1:
            search = False
        for _ in range(3):
            pa.click(x=960, y=832)
        time.sleep(0.3)
    print("Next button found")

    # Click next button
    if pos[0] != -1:
        click_image(folder+"next.png", pos, "left", 0.5)
    print("Next button clicked")

def handle_post_duel():
    #
    # POST GAME
    #
    # Try character
    find_and_click(folder + "char_"+character+".png", timeout=10, click_delay=0.5)

def handle_replay():
    #
    # EDGE CASE IF REPLAY IS NEEDED IN BATTLE
    # 
    # check for replay
    if replay_click(folder+"replay.png", folder+"yes.png", 1):
        time.sleep(3)
    pos = imagesearch(folder+"battle_phase_status.png")
    if pos[0] == -1:
        pass # fix this later 

def connection_drop():
    #
    # EDGE CASE IF CONNECTION DROPS
    #
    # click retry if connection breaks
    find_and_click(folder + "retry.png", timeout=1, click_delay=0.5)


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

"""def handle_draw_phase():
    start = time.time()

    while time.time() - start < 3:
        if imagesearch(folder+"main_phase.png")[0] > -1:
            return True  # success

        if imagesearch(folder+"draw_phase.png")[0] > -1:
            pa.click(960, 832)

        time.sleep(0.08)

    return False

This:

    Clicks only when draw phase is visible

    Stops as soon as main phase appears

    Survives lag, fades, and missed clicks
"""
    

### THESE ARE SOME FUNCTIONS TO INCORPORATE LATER ###

# caching images
def get_state_images(image_list, folder):
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

# Separate click and confirm to two functions
def click_target(find_img=None, coords=None, min_clicks=1, timeout=2, folder="./images/"):
    start = time.time()
    clicks = 0

    while clicks < min_clicks and time.time() - start < timeout:
        pos = coords if coords else imagesearch(folder + find_img)

        if pos and (coords or pos[0] != -1):
            pa.click(*pos)
            clicks += 1
            time.sleep(0.3)
        else:
            time.sleep(0.1)

    return clicks > 0

def confirm_state(confirm_appear=None, confirm_gone=None, timeout=2, folder="./images/"):
    start = time.time()

    while time.time() - start < timeout:

        if confirm_appear:
            pos = imagesearch(folder + confirm_appear)
            if pos and pos[0] != -1:
                return True

        if confirm_gone:
            pos = imagesearch(folder + confirm_gone)
            if not pos or pos[0] == -1:
                return True

        time.sleep(0.1)

    return False

# Then combine them like this:
def click_and_confirm(args):
    if click_target(...):
        return confirm_state(...)
    return False

"""
Why This Is Better:

Each function does ONE job

Easier to debug

Easier to test

Reusable

This is clean design.

"""

# Optimized Version (Minimum Image Searches)
"""
Here's a version that:

Searches once per loop

Doesn't double-search in confirm

Minimizes wasted scans
"""
def click_and_confirm_fast(
    find_img=None,
    coords=None,
    confirm_img=None,
    timeout=2,
    min_clicks=1,
    folder="./images/"
):

    if not find_img and not coords:
        raise ValueError("Need find_img or coords")

    start = time.time()
    clicks = 0

    while time.time() - start < timeout:

        # Search once
        pos = coords if coords else imagesearch(folder + find_img)

        if pos and (coords or pos[0] != -1):

            if clicks < min_clicks:
                pa.click(*pos)
                clicks += 1
                time.sleep(0.3)

            # After clicking enough, check confirm
            if confirm_img:
                confirm_pos = imagesearch(folder + confirm_img)
                if confirm_pos and confirm_pos[0] != -1:
                    return True
            else:
                return True

        time.sleep(0.1)

    return False
"""
Why This Is Faster:
Instead of:

Click phase searches
Confirm phase searches


It merges both into a single loop.

Fewer image scans.

Much faster.

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


    

 

    

    




