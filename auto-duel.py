from imagesearch import *
import pyautogui as pa
import time


def find_and_click(image_path, timeout=1, click_delay=0.5):
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

def click_until_next(current_img, next_img, click_pos, timeout=3):
    start = time.time()

    while time.time() - start < timeout:
        if imagesearch(next_img)[0] > -1:
            return True
        
        if imagesearch(current_img)[0] > -1:
            pa.click(*click_pos)

        time.sleep(0.1)

    return False


folder = "./image/"
character = "arrow"

total_duel = 100



for i in range(total_duel):

    # Try duel button for 1 sec
    find_and_click(folder + "duel.png", timeout=10, click_delay=0.5)

    # Try character for 1 sec
    find_and_click(folder + "char_"+character+".png", timeout=10, click_delay=0.5)

    # Try duel button for 1 sec
    find_and_click(folder + "duel.png", timeout=10, click_delay=0.5)

    print("waiting...")

    find_and_click(folder + "draw_phase.png", timeout=10, click_delay=0.5)


    # Summon monster
    monster_count = 0

    # Loop starts here
    finished = False

    while not finished:

        print("Draw phase clicker running...")

        CLICK_INTERVAL = 0.2
        MAX_RUNTIME = 15  # or however long this logic should be active

        start = time.time()
        allow_click = False

        while time.time() - start < MAX_RUNTIME:

            draw_visible = imagesearch(folder + "draw_phase.png")[0] != -1
            main_visible = imagesearch(folder + "main_phase.png")[0] != -1

            # If main phase is visible → stop clicking
            if main_visible:
                allow_click = False

            # If draw phase is visible → allow clicking
            if draw_visible:
                allow_click = True

            # Click ONLY if draw is visible AND we're allowed to click
            if allow_click and draw_visible:
                find_and_click(
                    folder + "draw_phase.png",
                    timeout=0.3,
                    click_delay=0.2
                )

            time.sleep(CLICK_INTERVAL)

        
        if monster_count < 2:
            print("summon")

            start_time = time.time()
            timeout = 30
            while True:
                pa.click(x=1056, y=850)
                time.sleep(0.1)

                pos = imagesearch(folder+"normal_summon.png")

                if pos[0] != -1:
                    print("Normal summon button found:", pos)
                    click_image(folder+"normal_summon.png", pos, "left", 0.1)
                    monster_count += 1
                    print("done summoning")
                    break

                if time.time() - start_time > timeout:
                    print("Timeout waiting for normal summon button")
                    break                

        # Find action button
        pos = imagesearch_loop(folder+"action.png", 0.1)
        print("Action button found : ", pos[0], pos[1])

        # Click action button
        if pos[0] != -1:
            click_image(folder+"action.png", pos, "left", 0.15)
        print("Action button clicked")

        # Find battle phase button
        time.sleep(0.5)
        pos = imagesearch(folder+"battle_phase.png")
        if pos[0] != -1:
            print("Battle phase button found : ", pos[0], pos[1])
            # Click battle phase button
            click_image(folder+"battle_phase.png", pos, "left", 0.1)
            print("Battle phase button clicked")
        else:
            # You can't attack if you get the first turn
            pos = imagesearch_loop(folder+"end_phase.png", 0.1)
            # Click end phase button
            if pos[0] != -1:
                click_image(folder+"end_phase.png", pos, "left", 0.1)
            print("End phase button clicked")

            # Skip battle phase
            continue

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

            # Check if finished
            time.sleep(3)
            pos = imagesearch(folder+"battle_phase_status.png")
            if pos[0] == -1:
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
                
            # Check if finished
            time.sleep(3)
            pos = imagesearch(folder+"battle_phase_status.png")
            if pos[0] == -1:
                break

        if not finished:
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
            
    # click retry if connection breaks
    find_and_click(folder + "retry.png", timeout=1, click_delay=0.5)
        
    # Wait ok button
    search = True
    while search:
        pos = imagesearch(folder+"ok.png")
        if pos[0] != -1:
            search = False
        for i in range(3):
            pa.click(x=1111, y=461) # should be right
        time.sleep(0.2)
    print("OK button found")

    # Click ok button
    if pos[0] != -1:
        click_image(folder+"ok.png", pos, "left", 0.1)
    print("OK button clicked")

    # Wait next button
    search = True
    while search:
        pos = imagesearch(folder+"next.png")
        if pos[0] != -1:
            search = False
        for i in range(3):
            pa.click(x=960, y=832)
        time.sleep(0.3)
    print("Next button found")

    # Click next button
    if pos[0] != -1:
        click_image(folder+"next.png", pos, "left", 0.5)
    print("Next button clicked")

    # Wait next button
    search = True
    while search:
        pos = imagesearch(folder+"next.png")
        if pos[0] != -1:
            search = False
        for i in range(3):
            pa.click(x=960, y=832)
        time.sleep(0.3)
    print("Next button found")

    # Click next button
    if pos[0] != -1:
        click_image(folder+"next.png", pos, "left", 0.5)
    print("Next button clicked")

    # Try character for 1 sec
    find_and_click(folder + "char_"+character+".png", timeout=10, click_delay=0.5)


