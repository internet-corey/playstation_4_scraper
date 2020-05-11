# The step-wise directions to turn on and scrape the ps4 console storefront

# stdlib
import os
import subprocess
import time

# 3rd party
import pyautogui

# files
import functions as fn
import directory_vars as v


def cap_store(run, mp):
    location = 'store'
    recal = 1
    fn.recalibrate(location)
    print(f'Navigating to {location} location')
    fn.press('esc')
    time.sleep(1)
    fn.press('left')
    # toggles back and forth variable number of times to grab all promos
    for i in range(mp):
        print(f'Pass {i+1} of {mp}')
        time.sleep(2)
        for i in range(3):
            fn.press('down')
        fn.ss(run, location)
        fn.press('esc')
        fn.press('right')
        time.sleep(1)
        fn.press('left')
        recal += 1
        if recal > 20:
            recal = 1
            fn.recalibrate(location)


def cap_psnow(run):
    location = 'psnow'
    print(f'Navigating to {location} location')
    fn.recalibrate(location)
    time.sleep(5)
    for i in range(5):
        fn.press('right')
        fn.ss(run, location)


def cap_feat_wh(run, mp):

    # whats hot
    location = 'whats_hot'
    n = 2
    fn.recalibrate(location, n=n)
    print(f'Executing main {location} rotation')
    fn.press('right')
    fn.ss(run, f'{location}_one')
    for i in range(3):
        fn.press('right')
    fn.ss(run, f'{location}_ng')
    for i in range(4):
        fn.press('right')
    fn.press('up')
    fn.ss(run, f'{location}_big_1')
    fn.press('down')
    fn.press('right')
    fn.ss(run, f'{location}_ec')
    for i in range(2):
        fn.press('right')
    fn.press('up')
    fn.ss(run, f'{location}_big_2')
    fn.press('down')
    fn.press('right')
    fn.ss(run, f'{location}_dls')
    fn.press('right')
    fn.press('right')
    fn.press('up')
    fn.ss(run, f'{location}_big_3')
    fn.press('down')
    fn.press('left')
    fn.slow_press('esc')

    # feat/wh carousel rotations
    recal = 1
    location = 'featured'
    print(f'Navigating to {location} location')
    fn.slow_press('up')
    for i in range(mp):
        print(f'Pass {i+1} of {mp}')
        fn.slow_press('right')
        fn.slow_press('up')
        fn.ss(run, location)
        fn.slow_press('down')
        fn.slow_press('left')
        location = 'whats_hot'
        print(f'Navigating to {location} location')
        fn.slow_press('down')
        fn.slow_press('right')
        fn.ss(run, f'{location}_one')
        for i in range(7):
            fn.press('right')
        fn.press('up')
        fn.ss(run, f'{location}_big_1')
        fn.press('down')
        fn.press('left')
        fn.slow_press('esc')
        location = 'featured'
        print(f'Navigating back to {location} location')
        fn.slow_press('up')
        recal += 1
        if recal > 25:
            recal = 1
            fn.recalibrate(location)


def cap_deals(run):
    location = 'deals'
    n = 3
    fn.recalibrate(location, n=n)
    fn.press('right')
    fn.ss(run, f'{location}_one')
    for i in range(4):
        fn.press('right')
    fn.ss(run, f'{location}_gd')
    for i in range(3):
        fn.press('right')
    fn.ss(run, f'{location}_ppd')
    fn.press('esc')


def cap_pop(run):
    location = 'popular'
    n = 4
    fn.recalibrate(location, n=n)
    fn.press('right')
    fn.ss(run, f'{location}_one')
    for i in range(4):
        fn.press('right')
    fn.ss(run, f'{location}_ts')
    for i in range(4):
        fn.press('right')
    fn.ss(run, f'{location}_mpg')
    fn.press('esc')


def cap_branded(run):
    location = 'branded'
    n = 6
    fn.recalibrate(location, n=n)

    # this location can have varying promo numbers, but 3 seems the max
    for i in range(3):
        location = f'branded_{i+1}'
        fn.press('right')
        fn.press('up')
        fn.press('up')
        fn.ss(run, location)
        fn.press('down')
        fn.press('down')

        # tries to go to the right, in case the promo has
        # multiple pages
        for i in range(7):
            fn.press('right')
            fn.ss(run, location)
        fn.press('esc')
        fn.slow_press('left')
        fn.slow_press('down')


def cap_free(run, mp):
    location = 'free'
    n = 7
    recal = 1
    fn.recalibrate(location, n)
    print(f'Executing multi-promo placement rotation')
    for i in range(mp):
        print(f'Pass {i+1} of {mp}')
        fn.press('right')
        fn.press('right')
        fn.ss(run, location)
        fn.press('left')
        fn.slow_press('left')
        fn.slow_press('up')
        fn.slow_press('down')
        recal += 1
        if recal > 20:
            recal = 1
            fn.recalibrate(location, n)


def cap_addons(run, mp):
    location = 'addons'
    n = 10
    recal = 1
    fn.recalibrate(location, n)
    print(f'Executing multi-promo placement rotation')
    for i in range(mp):
        print(f'Pass {i+1} of {mp}')
        fn.press('right')
        fn.press('right')
        fn.ss(run, location)
        fn.press('left')
        fn.slow_press('left')
        fn.slow_press('up')
        fn.slow_press('down')
        recal += 1
        if recal > 20:
            recal = 1
            fn.recalibrate(location, n)


def cap_plus(run):
    location = 'psplus'
    n = 14
    fn.recalibrate(location, n)
    fn.ss(run, location)


def cap_games(run, mp):
    recal = 1
    location = 'games'
    n = 11
    fn.recalibrate(location, n)
    fn.slow_press('right')
    fn.press('right')
    fn.ss(run, f'{location}_eg')
    for i in range(3):
        fn.press('right')
    fn.ss(run, f'{location}_mp')
    for i in range(2):
        fn.press('right')
    fn.press('up')
    fn.ss(run, f'{location}_big_1')
    fn.press('down')
    fn.press('right')
    fn.ss(run, f'{location}_oop')
    for i in range(4):
        fn.press('right')
    fn.press('up')
    fn.ss(run, f'{location}_big_2')
    fn.press('down')
    fn.press('left')
    fn.slow_press('esc')

    # carousel rotations
    for i in range(mp):
        print(f'Pass {i+1} of {mp}')
        fn.press('right')
        fn.ss(run, f'{location}_eg')
        for i in range(7):
            fn.press('right')
        fn.press('up')
        fn.ss(run, f'{location}_big_1')
        fn.press('down')
        fn.press('left')
        fn.slow_press('esc')
        fn.slow_press('down')
        fn.press('right')
        fn.press('up')
        fn.ss(run, f'{location}_ft')
        fn.press('down')
        fn.slow_press('left')
        fn.slow_press('up')
        recal += 1
        if recal > 20:
            recal = 1
            fn.recalibrate(location, n)
            fn.slow_press('right')


def scrape_ps4(run, mp=50):
    '''
    Runs through the full scrape.
    '''

    # setup
    os.makedirs(v.wd, exist_ok=True)
    os.makedirs(v.tmp_dir, exist_ok=True)
    os.makedirs(v.ref_dir, exist_ok=True)
    print('Opening remote play, one moment please...')
    rp = subprocess.Popen('example/filepath/ps4_scraper/RemotePlay/RemotePlay.exe')

    time.sleep(10)
    fn.set_fg('PS4 Remote Play')
    fn.press('tab')
    fn.press('enter')
    print('Waiting 90 seconds for PS4 to turn on...')
    time.sleep(90)
    fn.set_fg('PS4 Remote Play')
    pyautogui.hotkey('alt', 'enter')
    time.sleep(2)

    # the scrape
    print('RUNNING FULL SCRAPE')
    cap_store(run, mp)
    cap_psnow(run)
    cap_feat_wh(run, mp)
    cap_deals(run)
    cap_pop(run)
    cap_branded(run)
    cap_free(run, mp)
    cap_addons(run, mp)
    cap_plus(run)
    cap_games(run, mp)

    # restart console
    print('Restarting the PS4')
    pyautogui.moveTo(960, 1040)
    time.sleep(1)
    pyautogui.mouseDown()
    time.sleep(1)
    pyautogui.mouseUp()
    time.sleep(1)
    pyautogui.moveTo(840, 500)
    fn.slow_press('right')
    for i in range(4):
        fn.press('down')
    print('Closing PS4 Remote Play App...')
    rp.kill()
    time.sleep(2)
