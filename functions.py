# stdlib
import os
import shutil
from glob import glob
import time
from datetime import date, datetime, timedelta

# 3rd party
import pyautogui
import win32gui
from PIL import Image, ImageGrab
from imagehash import phash
from pandas import DataFrame, read_csv

# files
import locations as locs
import directory_vars as v
import scraper_steps as steps


def set_fg(name):
    '''
    makes sure specified app is foreground window
    '''
    wnd = win32gui.FindWindow(None, name)
    win32gui.SetForegroundWindow(wnd)
    time.sleep(2)


def press(key):
    '''
    pyautogui's press function wasn't reliable, made my own to ensure it works.
    '''
    pyautogui.keyDown(key)
    pyautogui.keyUp(key)
    time.sleep(.5)


def slow_press(key):
    '''
    certain rotations prone to store skipping sections. a slower key press for
    those.
    '''
    pyautogui.keyDown(key)
    pyautogui.keyUp(key)
    time.sleep(1.5)


def nav_top(n, location):
    '''
    moves to top of nav-bar, then moves down n times to next location.
    '''
    print('Navigating to top of menu')
    for i in range(10):
        press('up')
    time.sleep(1)
    print(f'Navigating to {location} location')
    for i in range(n):
        press('down')
    time.sleep(2)


def nav_bottom(n, location):
    '''
    moves to bottom of nav-bar then moves up n times to next location.
    '''
    print('Navigating to bottom of menu')
    pyautogui.keyDown('down')
    time.sleep(7)
    pyautogui.keyUp('down')
    time.sleep(1)
    print(f'Navigating to {location} location')
    for i in range(n):
        slow_press('up')
    time.sleep(2)


def ss(run, location):
    '''
    takes a location as argument, gets a time stamp, takes screenshot
    and saves file.
    '''
    time.sleep(.6)
    print('Taking screenshot')
    ts = time.strftime('%I%M%S', time.localtime())
    fp = f'{v.tmp_dir}/{location}-{ts}-{run}.jpg'
    ImageGrab.grab().save(fp, 'JPEG')


def recalibrate(location, n=0):
    '''
    Recalibrates, goes back to main menu and re-navigates to location, as a
    potential redundant move, to make sure the scraper isn't taking
    screenshots of the wrong location.
    '''
    navtop_list = [
        'whats_hot',
        'deals',
        'popular',
        'branded'
    ]
    print('Recalibrating, please stand by...')
    pyautogui.moveTo(960, 1040)
    time.sleep(2)
    pyautogui.mouseDown()
    pyautogui.mouseUp()
    time.sleep(2)
    pyautogui.moveTo(840, 500)
    pyautogui.keyDown('left')
    time.sleep(3)
    pyautogui.keyUp('left')

    # different logic for nagivating to various locations
    if location.lower() == 'store':
        pass
    elif location.lower() == 'psnow':
        press('right')
        press('right')
        press('enter')
        time.sleep(5)
    elif location.lower() == 'featured':
        press('enter')
        time.sleep(5)
    elif location.lower() in navtop_list:
        press('enter')
        time.sleep(5)
        nav_top(n, location)
    else:
        press('enter')
        time.sleep(5)
        nav_bottom(n, location)


def dupe_remover(wd, location):
    '''
    Checks image files per location keyword for duplicate whole images. Done
    prior to the new_promo_check to reduce number of total images.
    '''
    print(f'removing dupes from {location}')
    image_dict = {}
    unique_images = {}
    duplicate_images = {}
    image_files = f'{wd}/*.jpg'

    for img in glob(image_files):
        imname = os.path.basename(img)

        # only loads in images if they are in the specified section
        if location in imname:
            coords = locs.duper_crops[location]
            image = Image.open(img).convert('L').crop(coords)
            image_dict[imname] = image

    while len(image_dict) > 0:

        # grab the first image
        # and comapre it against every other image we have
        image_name = list(image_dict.keys())[0]
        image = image_dict[image_name]
        duplicate_to_this_image = []
        for other_image_name, other_image in image_dict.items():
            if image_name == other_image_name:
                continue

            # if the image is a duplicate, remove it from the image dictionary
            # and delete the file
            p = phash(image)
            p_other = phash(other_image)
            delta = p - p_other
            if delta < 7:
                other_file = f'{wd}/{other_image_name}'
                os.remove(other_file)
                duplicate_to_this_image.append(other_image_name)

        for dupe_name in duplicate_to_this_image:
            dupe_image = image_dict[dupe_name]
            del image_dict[dupe_name]
            duplicate_images[dupe_name] = dupe_image

        # Now that we've compared the image
        # It should be considered unique
        unique_images[image_name] = image
        del image_dict[image_name]


def get_id_dict(retailer):
    '''creates dict from retailer's ID CSV file
    '''
    print('getting ID dict')
    idfile = 'example/filepath/{retailer}_scraper/reference_directory/{retailer}_ids.csv'
    df = read_csv(idfile)
    d = df.set_index('hash_id').to_dict()['phash']
    return d


def gen_id(retailer, phash, hash_dict):
    '''generates a unique ID for a promo image.
    '''
    if retailer == 'PS4':
        mod = 'P_'
    elif retailer == 'XB1':
        mod = 'X_'
    latest_id = max(hash_dict)
    newid = latest_id + 1
    hash_dict[newid] = phash
    rid = mod + str(newid)

    return rid


def update_id_dict(retailer, hash_dict):
    '''updates retailer's hash ID file with new entries from latest scrape
    '''
    print('updating ID file')
    idfile = 'example/filepath/{retailer}_scraper/reference_directory/{retailer}_ids.csv'
    df = DataFrame(
        list(hash_dict.items()),
        columns=['hash_id', 'phash']
    )
    df.to_csv(idfile, index=False)


def exclusivity_check(wd, location, run):
    '''checks sponsored placements for half-day/full-day exclusivity or
    a carousel of promotions.
    returns full, half, or crsl for locations with sponsored placements,
    returns None for locations without sponsored placements or locations with
    no images in the work dir.
    '''

    skip_locs = [
        'branded',
        'deals_gd',
        'deals_one',
        'deals_ppd',
        'games_big_2',
        'games_mp',
        'games_oop',
        'popular_mpg',
        'popular_one',
        'popular_ts',
        'psplus',
        'psnow',
        'whats_hot_big_2',
        'whats_hot_dls',
        'whats_hot_ng',
        'whats_hot_po'
    ]
    fullpage_locs = [
        'featured',
        'games_ft',
        'games_big_1',
        'whats_hot_big_1'
    ]
    if location in skip_locs:
        return None
    else:
        images = f'{wd}/{run}_run_originals/*.jpg'

        # different crop coords dict key naming scheme for different locations
        if location in fullpage_locs:
            coords = locs.promo_crops[location]['1']
        elif location == 'store':
            coords = locs.promo_crops[location]['big_1']
        else:
            coords = locs.promo_crops[location]['spon']
        promos = [img for img in glob(images) if location in img]
        if not promos:
            return None
        else:
            print(f'  checking exclusivity for {location} sponsored promos')
            unique = True
            for promo in promos:
                others = [img for img in promos if promo not in img]
                image = Image.open(promo).convert('L').crop(coords)
                p = phash(image)
                for other in others:
                    otherimage = Image.open(other).convert('L').crop(coords)
                    p_other = phash(otherimage)
                    delta = p - p_other
                    if delta > 5:
                        unique = False
                        break
                if not unique:
                    break

            if unique:
                if run == 'second':
                    full = True
                    first_dir = f'{wd}/first_run_originals/*.jpg'
                    first = [img for img in glob(first_dir) if location in img]
                    for promo in first:
                        otherim = Image.open(promo).convert('L').crop(coords)
                        p_other = phash(otherim)
                        delta = p - p_other
                        if delta > 5:
                            full = False
                            break
                    if full:
                        return 'full'
                    else:
                        return 'half'
                else:
                    return 'half'
            else:
                return 'crsl'


def new_promo_checker(wd, location, run, hash_dict):
    '''
    Checks for new/existing promos.
    '''
    print(f'checking {location} {run} run for new/existing promos')

    # gets datestamps for today and yesterday
    today = date.today()
    yesterday = date.today() - timedelta(days=1)
    today = today.strftime('%m-%d-%y')
    yesterday = yesterday.strftime('%m-%d-%y')

    # directory and image file variables
    run_dir = f'{wd}/{run}_run_originals'
    originals_dir = f'{wd}/combined_originals'
    ref_loc_dir = f'{v.ref_dir}/{location}'
    ref_loc_archive = f'{ref_loc_dir}/archive'
    ended_dir = f'{wd}/ended_{yesterday}'

    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(ended_dir, exist_ok=True)
    os.makedirs(ref_loc_dir, exist_ok=True)
    os.makedirs(ref_loc_archive, exist_ok=True)

    wd_images = f'{wd}/*.jpg'
    run_images = f'{run_dir}/*.jpg'
    originals = f'{originals_dir}/*.jpg'
    ref_images = f'{ref_loc_dir}/*.jpg'

    # checks sponsored placement exclusivity for location
    excl = exclusivity_check(wd, location, run)

    # changes the promo with 'half' exclusivity keyword to 'full' in work dir
    # and ref dir
    if excl == 'full':
        wdims = [
            im for im in glob(wd_images) if location in im and 'half' in im
        ]
        if wdims:
            wdim = wdims[0]
            basename = os.path.basename(wdim)
            loc, place, scraperun, pid = basename.split('-')
            newname = f'{loc}-{place}-full-{pid}'
            new_wdim = f'{wd}/{newname}'
            os.replace(wdim, new_wdim)
            refim = [im for im in glob(ref_images) if pid in im][0]
            new_refim = f'{ref_loc_dir}/{newname}'
            os.replace(refim, new_refim)

    new = [img for img in glob(run_images) if location in img]
    active = [img for img in glob(ref_images)]

    # CHECKING NEW IMAGES
    print('  checking new images')
    for img in new:
        imname = os.path.basename(img)
        splitname = os.path.splitext(imname)[0]

        # dict of crop coords for all placements in the location
        crops = locs.promo_crops[location]

        for placement in crops:
            is_new = True
            coords = crops[placement]

            # loads, greyscales, crops image, gets perception hash
            image = Image.open(img).convert('L').crop(coords)
            p = phash(image)

            # checks cropped image against images in reference directory
            for refimg in glob(ref_images):
                refname = os.path.basename(refimg)
                refimage = Image.open(refimg)

                # checks size and skips if different-sized images
                w1, h1 = image.size
                wr, hr = refimage.size
                if .75 > (w1 / wr) > 1.25:
                    continue

                # delta between image and refimage's perception hashes
                pref = phash(refimage)
                delta = p - pref

                # ends the loop if an active image matches the new image.
                if delta < 7:
                    is_new = False
                    break

            # promo is new. copies full image to work dir
            # and cropped image to ref dir
            if is_new:
                print(f'  {imname} {placement} is new')
                loc, ts, scraperun = splitname.split('-')

                # modifies scraperun to include exclusivity keyword if exists
                # and is for location or placement w/ sponsored ads
                fp_list = [
                    'featured',
                    'games_big_1',
                    'games_ft',
                    'whats_hot_big_1'
                ]
                if excl is not None:
                    if location in fp_list or placement == 'spon':
                        if excl == 'full':
                            scraperun == 'full'
                        else:
                            scraperun = f'{scraperun}_{excl}'

                # generates a new ID, saves full and cropped files of new promo
                pid = gen_id('PS4', p, hash_dict)
                promoname = f'{loc}-{placement}-{scraperun}-{pid}.jpg'
                promo_fpath = f'{wd}/{promoname}'
                fpath_cropped = f'{ref_loc_dir}/{promoname}'
                image.save(fpath_cropped)
                shutil.copy2(img, promo_fpath)
            else:
                print(f'  {imname} {placement} is active')

    # CHECKING ACTIVE IMAGES
    print('  checking active images')
    for refimg in active:
        refname = os.path.basename(refimg)
        refimage = Image.open(refimg)

        # dict of crop coords for all placements in the location
        crops = locs.promo_crops[location]
        is_ended = True

        # extract placement from ref_image filename
        trash1, placement, trash2, trash3 = refname.split('-')

        # dict of crop coords for all placements in the location
        crops = locs.promo_crops[location]

        for img in glob(originals):
            if location in img:

                # goes through each placement to compare the images
                for placement in crops:

                    # 4-item tuple from location's crop dict
                    coords = crops[placement]

                    # loads, greyscales, and crops image
                    image = Image.open(img).convert('L').crop(coords)

                    # checks size and skips if different-sized images
                    w1, h1 = image.size
                    wr, hr = refimage.size
                    if .75 > (w1 / wr) > 1.25:
                        continue

                    # difference hash for image and reference, and delta
                    p = phash(image)
                    p_ref = phash(refimage)
                    delta = p - p_ref

                    # ends the loop if a new image matches the active image
                    if delta < 7:
                        is_ended = False
                        break

                if not is_ended:
                    break

        # the active promo didn't match any new promos. the active promo
        #  has ended
        if is_ended:
            print(f'  {refname} is ended')
            shutil.copy2(refimg, ended_dir)

            # moves file from ref dir to the archive
            shutil.copy2(refimg, ref_loc_archive)
            os.remove(refimg)


def promo_checks(wd=v.wd):
    '''after both daily scrape runs are complete, this runs through various
    functions to check for new/existing and ended promos, and to check
    sponsored placement half/full exclusivity vs carousel. will end with only
    image files of new promos to work through, and a folder of ended promos to
    mark end dates for.
    '''

    # # adds originals from all runs to a combined dir for checking active
    # # editorial promos
    originals_dir = f'{wd}/combined_originals'
    os.makedirs(originals_dir, exist_ok=True)
    for fol in os.listdir(wd):
        folder = os.path.join(wd, fol)
        if os.path.isdir(folder):
            if 'originals' in folder and 'combined' not in folder:
                for f in os.listdir(folder):
                    if '.jpg' in f:
                        promo = os.path.join(folder, f)
                        shutil.copy2(promo, originals_dir)

    hash_dict = get_id_dict('PS4')

    # first run
    for location in locs.promo_crops:
        new_promo_checker(wd, location, 'first', hash_dict)
    time.sleep(1)

    # second run
    for location in locs.promo_crops:
        new_promo_checker(wd, location, 'second', hash_dict)
    time.sleep(1)

    update_id_dict('PS4', hash_dict)

    shutil.rmtree(originals_dir)


def scrape(run, mp=50):
    start = datetime.now()
    steps.scrape_ps4(run, mp)
    stop = datetime.now()
    for location in locs.promo_crops:
        dupe_remover(v.tmp_dir, location)
    run_dir = f'{v.wd}/{run}_run_originals'
    os.rename(v.tmp_dir, run_dir)
    if run == 'second':
        promo_checks()
    print('TOTAL TIME', stop - start)
