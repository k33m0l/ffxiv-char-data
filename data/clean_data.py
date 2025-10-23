import pandas
import glob
import os

PATH = '../resources/raw/'

all_files = glob.glob(os.path.join(PATH, '*.csv'))

# Combine all files into one
for file in all_files:
    df = pandas.read_csv(file)
    full_df = df


full_df = full_df.drop(columns=['error', 'status', 'id'])

def merge_duplicate_job(short_name: str, low_lvl_name: str, high_lvl_name: str):
    global full_df
    full_df[short_name] = full_df[high_lvl_name].where(full_df[high_lvl_name].notna(), full_df[low_lvl_name])

def clean_job(short_name: str):
    global full_df
    full_df[short_name] = full_df[short_name].where(full_df[short_name].ne('-'), 0).fillna(0.0).astype(int)

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

print(full_df.columns.values)
print(full_df)
