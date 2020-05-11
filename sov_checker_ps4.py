'''new way to check exclusivity (share of voice) per client meetings.
(not yet implemented)
'''

# stdlib
from glob import glob
import argparse
import os

# 3rd party
import pyodbc
from PIL import Image
from imagehash import phash
from pandas import DataFrame, read_sql

# files
import locations as locs


def fourther(ratio):
    '''modifies a float to the closest fourth
    '''
    if ratio > .25:
        ratio = .25
    elif .25 < ratio < .5:
        low = ratio - .25
        high = .5 - ratio
        if low < high:
            ratio = .25
        else:
            ratio = .5
    elif .5 < ratio < .75:
        low = ratio - .5
        high = .75 - ratio
        if low < high:
            ratio = .5
        else:
            ratio = .75
    elif .75 < ratio < 1:
        ratio = .75

    return ratio


def sov_check(wd, location, active_list):
    '''checks work dir / location for share of voice.
    wd: file directory; location: str keyword;
    active_list: [(CampaignId, EntityId, HashValue)].
    returns a list of tuples [(CampaignId, ShareOfVoice)].
    '''

    fullpage_locs = [
        'featured',
        'games_ft',
        'games_big_1',
        'whats_hot_big_1'
    ]
    imgs = f'{wd}/originals/*.jpg'
    sov_list = []

    # different crop coords dict key naming scheme for different locations
    if location in fullpage_locs:
        coords = locs.promo_crops[location]['1']
    elif location == 'store':
        coords = locs.promo_crops[location]['big_1']
    else:
        coords = locs.promo_crops[location]['spon']

    total_count = 0
    for img in glob(imgs):
        if location in img:
            imname = os.path.splitext(os.path.basename(img))
            trash1, trash2, count = imname.split('-')
            count = int(count)
            total_count += count

    # list of tuples, image filepath and its perception hash
    promos = [
        (img, phash(Image.open(img).crop(coords)))
        for img in imgs if location in img
    ]

    # for each tup in the active list, goes thru each image in promos. if the
    # perception hashes match, adds campaign ID and share of voice to the
    # sov_list.
    for cid, eid, ph in active_list:
        for img, ph2 in promos:
            if ph == ph2:
                imname = os.path.splitext(os.path.basename(img))
                trash1, trash2, count = imname.split('-')
                count = int(count)
                sov = count / total_count
                sov = fourther(sov)
                sov_list.append((cid, sov))

    return sov_list


def sov_db_updater(wd):
    '''updates DB from list of campaign_id/sov.
    wd: file directory.
    '''

    node_ids = {
        'addons': 1,
        'branded': 1,
        'featured': 1,
        'free': 1,
        'games_big_1': 1,
        'games_eg': 1,
        'games_ft': 1,
        'store': 1,
        'whats_hot_big_1': 1,
        'whats_hot_one': 1,
    }
    discard, date = wd.split('ps4_console_scraper/ps4_')

    # db connection + SQL queries
    conn = pyodbc.connect(
        '''
        Driver={ODBC Driver 17 for SQL Server};
        Server=.;
        Database=DMT;
        Trusted_Connection=yes;
        '''
    )
    cursor = conn.cursor()

    # active campaigns for a given sub-location on a given date
    active_sql = (
        '''
        USE DMT
        SELECT c.[CampaignId], p.[EntityId], h.[HashValue]
        FROM [RetailTracker].[Campaign] c
            JOIN [RetailTracker].[Promotion] p ON p.[CampaignId] = c.[CampaignId]
            JOIN [FAC_CampaignResults] subloc ON subloc.[CampaignId] = c.[CampaignId]
            JOIN [FAC_RetailTrackerResults] r ON r.[promotion_id] = p.[PromotionId]
            JOIN [RetailTracker].[PlacementHash] h on h.[HashId] = c.[HashId]
        WHERE c.[RetailerId] = 13
            AND subloc.[node_id] = ? AND subloc.[check_value] = 1
            AND r.[node_id] = '215198'
            AND (c.[StartDate] <= ? AND (c.[EndDate] >= ? OR c.[EndDate] IS NULL))
        '''
    )

    # updates share of voice table with new data
    sov_sql = (
        '''
        INSERT INTO [DMT].[RetailTracker].[ShareOfVoice] (CampaignId, ShareOfVoice, Date)
        VALUES (?, ?, ?);
        '''
    )

    # checks exclusivity and updates db for each location with a sponsored placement
    for location in node_ids:
        print(f'updating SOV for {location}')
        node_id = node_ids[location]

        # gets all active campaigns for given sublocation/date
        # and puts it into a pandas dataframe
        q = read_sql(
            active_sql,
            conn,
            params=(node_id, date, date)
        )
        df = DataFrame(q)

        # list of tuples [(CampaignId, EntityId, HashValue)] from the dataframe
        active_list = list(df.to_records(index=False))

        # list of campaign IDs and their exclusivity types
        results = sov_check(wd, location, active_list)

        # updates the db with the results
        cursor.executemany(sov_sql, results)
        print(f'updated {location} exclusivity for {date}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'directory',
        action='store',
        help='runs sov_db_updater fuction. arg is a directory'
    )
    args = parser.parse_args()

    if os.path.isdir(args.directory):
        sov_db_updater(args.directory)
    else:
        print('Error. Given argument is not a directory.')
