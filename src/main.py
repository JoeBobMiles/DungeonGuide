import csv, argparse, sys, math, re
import yaml

DATA_DIR = '../test_data/'

def csv_to_dict(filepath):
    '''
    Grabs the contents of the given CSV file and converts the retreived data
    into a list of dictionaries. Each entry in the returned dictionaries has a
    key corresponding to the values in the first row.

    @NOTE! This assumes that the first row in the CSV are the column names!
    '''

    data = list()

    with open(filepath) as f:
        for line in csv.reader(f):
            data.append(line)

    # Extract the header from the retreived values and remove it from the actual
    # data.
    header = data[:1][0]
    data = data[1:]

    # For each line, create a dictionary whose keys are the corresponding header
    # values for each entry in the row.
    for row_number, row in enumerate(data):
        tmp = dict()

        for column_number, value in enumerate(row):
            tmp[header[column_number]] = value

        data[row_number] = tmp

    return data

def parse_monster_balance_table(csv_data):
    '''
    This function takes in a list of dictionaries (retreived using csv_to_dict)
    and converts it into a data structure that encodes the monster balance table
    that is found in the Dungeon Master's Guide on page 274.
    '''

    def parse_range(string):
        '''
        This function parses a range expression (ie '123-456') and returns a
        list with the low and high values broken out (ie [123, 456]).
        '''
        return [ int(s) if s != '*' else math.inf for s in string.split('-') ]

    for row in csv_data:
        row['hitpoints'] = parse_range(row['hitpoints'])
        row['average_damage'] = parse_range(row['average_damage'])

        for k in [ 'proficiency_bonus','attack_bonus','armor_class','save_dc' ]:
            row[k] = int(row[k])

    return csv_data

def compute_cr(monster_data, balance_table):
    '''
    This computes monster CR based on the given monster stat-block and the
    monster balance table.
    '''

    def average_roll(expression):
        values = re.match(r'(\d+)d(\d+)([+-]\d+)', expression)
        values = [ int(i) if i else 0 for i in values ]

        minimum = values[0]
        maximum = values[0]*values[1] + values[2]

        # This will round down instead of up
        return int((minimum + maximum) / 2)

    # Compute Defensive CR.
    defensive_cr = 0

    #   Compute CR from HP.
    for entry in balance_table:

        avg = average_roll(mosnter_data['hp'])

        if avg >= entry['hitpoints'][0] and avg <= entry['hitpoints'][1]:
            defensive_cr = entry['cr']
            break

    #   Compute CR Offset from AC.
    cr_from_ac = 0

    for entry in balance_table:
        if monster_data['armor']['class'] == entry['armor_class']:
            cr_from_ac = entry['cr']
            break

    # Another place where we're rounding down. I don't know if that's a good
    # thing...
    defensive_cr = defensive_cr - int((defensive_cr - cr_from_ac) / 2)

    # Compute Offensive CR.
    offensive_cr = 0

    #   Compute CR from Average Damage.
    '''
    After a long time of looking at how to compute average damage, I've come
    to the conclusion that this is a monsterously (heh) complicated problem
    that will take a very long time to formulate a ready solution for.
    '''
    for entry in balance_table:

        avg_dpr = 0

        for action in monster_data['actions']:
            avg_dpr = avg_dpr + average_roll(action['damage'])

        if avg >= entry['hitpoints'][0] and avg <= entry['hitpoints'][1]:
            defensive_cr = entry['cr']
            break

    #   Compute CR Offset from Attack Bonus (or save DC).

    # Compute Average CR. (Round to nearest CR)

def main():
    global DATA_DIR

    mosnter_block = None

    with open(DATA_DIR+'gargoyle.yaml') as f:
        monster_block = yaml.load(f)

    # print(monster_block)

    csv_data = csv_to_dict(DATA_DIR+'monster_balancing_table.csv')

    monster_balance_table = parse_monster_balance_table(csv_data)

if __name__ == '__main__':
    main()
