import pandas
import glob
import os

PATH = '../resources/raw/'
EXPORT_PATH = '../resources/cleaned.csv'

print("Merging all raw  csv together")
all_files = glob.glob(os.path.join(PATH, '*.csv'))
frames = [pandas.read_csv(file) for file in all_files]
full_df = pandas.concat(frames)

full_df = full_df.drop(columns=['error', 'status', 'id'])

def merge_duplicate_job(short_name: str, low_lvl_name: str, high_lvl_name: str):
    global full_df
    full_df[short_name] = full_df[high_lvl_name].where(full_df[high_lvl_name].notna(), full_df[low_lvl_name])

def clean_job(short_name: str):
    global full_df
    full_df[short_name] = full_df[short_name].where(full_df[short_name].ne('-'), 0).fillna(0.0).astype(int)

print("Merging and cleaning duplicate jobs")
merge_duplicate_job('PLD', 'Gladiator', 'Paladin / Gladiator')
merge_duplicate_job('WAR', 'Marauder', 'Warrior / Marauder')
merge_duplicate_job('DRG', 'Lancer', 'Dragoon / Lancer')
merge_duplicate_job('MNK', 'Pugilist', 'Monk / Pugilist')
merge_duplicate_job('BRD', 'Archer', 'Bard / Archer')
merge_duplicate_job('BLM', 'Thaumaturge', 'Black Mage / Thaumaturge')
merge_duplicate_job('WHM', 'Conjurer', 'White Mage / Conjurer')
merge_duplicate_job('NIN', 'Rogue', 'Ninja / Rogue')
merge_duplicate_job('SMN', 'Arcanist', 'Summoner / Arcanist')
merge_duplicate_job('SCH', 'Arcanist', 'Scholar')

clean_job('PLD')
clean_job('WAR')
clean_job('DRG')
clean_job('MNK')
clean_job('BRD')
clean_job('BLM')
clean_job('WHM')
clean_job('NIN')
clean_job('SMN')
clean_job('SCH')

print("Renaming and cleaning remaining jobs")
full_df['DRK'] = full_df['Dark Knight']
clean_job('DRK')
full_df['MCH'] = full_df['Machinist']
clean_job('MCH')
full_df['AST'] = full_df['Astrologian']
clean_job('AST')
full_df['SAM'] = full_df['Samurai']
clean_job('SAM')
full_df['RDM'] = full_df['Red Mage']
clean_job('RDM')
full_df['BLU'] = full_df['Blue Mage (Limited Job)']
clean_job('BLU')
full_df['GNB'] = full_df['Gunbreaker']
clean_job('GNB')
full_df['DNC'] = full_df['Dancer']
clean_job('DNC')
full_df['RPR'] = full_df['Reaper']
clean_job('RPR')
full_df['SGE'] = full_df['Sage']
clean_job('SGE')
full_df['VPR'] = full_df['Viper']
clean_job('VPR')
full_df['PCT'] = full_df['Pictomancer']
clean_job('PCT')

full_df['ALC'] = full_df['Alchemist']
clean_job('ALC')
full_df['ARM'] = full_df['Armorer']
clean_job('ARM')
full_df['BSM'] = full_df['Blacksmith']
clean_job('BSM')
full_df['CRP'] = full_df['Carpenter']
clean_job('CRP')
full_df['CUL'] = full_df['Culinarian']
clean_job('CUL')
full_df['GSM'] = full_df['Goldsmith']
clean_job('GSM')
full_df['LTW'] = full_df['Leatherworker']
clean_job('LTW')
full_df['WVR'] = full_df['Weaver']
clean_job('WVR')
full_df['BTN'] = full_df['Botanist']
clean_job('BTN')
full_df['FSH'] = full_df['Fisher']
clean_job('FSH')
full_df['MIN'] = full_df['Miner']
clean_job('MIN')

full_df = full_df.drop(columns=[
    'Gladiator',
    'Paladin / Gladiator',
    'Marauder',
    'Warrior / Marauder',
    'Lancer',
    'Dragoon / Lancer',
    'Pugilist',
    'Monk / Pugilist',
    'Archer',
    'Bard / Archer',
    'Thaumaturge',
    'Black Mage / Thaumaturge',
    'Conjurer',
    'White Mage / Conjurer',
    'Rogue',
    'Ninja / Rogue',
    'Arcanist',
    'Summoner / Arcanist',
    'Scholar',
    'Dark Knight',
    'Machinist',
    'Astrologian',
    'Samurai',
    'Red Mage',
    'Blue Mage (Limited Job)',
    'Gunbreaker',
    'Dancer',
    'Reaper',
    'Sage',
    'Viper',
    'Pictomancer',
    'Alchemist',
    'Armorer',
    'Blacksmith',
    'Carpenter',
    'Culinarian',
    'Goldsmith',
    'Leatherworker',
    'Weaver',
    'Botanist',
    'Fisher',
    'Miner',
])

print("Reformatting the remaining data")
# Format World and Data center data
full_df[['world', 'dc']] = full_df['world'].str.split(' ', expand=True)
full_df['dc'] = full_df['dc'].str.replace('\[{1}|\]{1}', '', regex=True)

# Format Race, Gender, and Clan
full_df[['Race/Clan', 'Gender']] = full_df['Race/Clan/Gender'].str.split(' / ', expand=True)
full_df['Gender'] = full_df['Gender'].str.replace('♀', 'Female')
full_df['Gender'] = full_df['Gender'].str.replace('♂', 'Male')

def split_race_clan(value, known_races):
    for race in known_races:
        if value.startswith(race):
            return pandas.Series([race, value[len(race):].strip()])
    return pandas.Series([None, value])

races = ["Miqo'te", 'Au Ra', 'Elezen', 'Hyur', 'Lalafell', 'Roegadyn', 'Viera', 'Hrothgar']
full_df['Race/Clan'] = full_df['Race/Clan'].fillna('Unknown')
full_df[['Race', 'Clan']] = full_df['Race/Clan'].apply(split_race_clan, known_races=races)


# Format faction and rank
full_df['Grand Company'] = full_df['Grand Company'].fillna('Unaligned / Unaligned')
full_df[['faction', 'rank']] = full_df['Grand Company'].str.split(' / ', expand=True)

full_df = full_df.drop(columns=['Race/Clan', 'Race/Clan/Gender', 'Grand Company']) 

# Format everything else
full_df['title'] = full_df['title'].fillna('')
full_df['pvp'] = full_df['pvp'].fillna('Unaligned')

# Drop duplicates when working of multiple csv
full_df.drop_duplicates(inplace=True)

print(full_df.columns.values)
print(full_df)

print("Exporting to CSV file")
full_df.to_csv(EXPORT_PATH, index=False)

