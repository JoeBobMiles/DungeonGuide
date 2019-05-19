import csv, argparse, sys, math, re, fractions
import yaml

DATA_DIR = './data/'

def csv_to_dict(filepath):
    '''
    Grabs the contents of the given CSV file and converts the retreived data
    into a list of dictionaries. Each entry in the returned dictionaries has a
    key corresponding to the values in the first row.

    NOTE[joe] This assumes that the first row in the CSV are the column names!
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
    and converts it into a data structure that encodes the monster balance
    table that is found in the Dungeon Master's Guide on page 274.
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
        values = re.match(r'(\d+)d(\d+)([+-]\d+)', expression).groups()
        values = [ int(i) if i else 0 for i in values ]

        minimum = values[0] + values[2]
        maximum = (values[0] * values[1]) + values[2]

        # This will round down instead of up
        return int((minimum + maximum) / 2)

    def cr_to_num(cr):
        cr_value = fractions.Fraction(cr)
        return cr_value.numerator / cr_value.denominator

    # Compute Defensive CR.
    defensive_cr = 0

    #   Compute CR from HP.
    avg = average_roll(monster_data['hitpoints'])
    for entry in balance_table:
        if avg >= entry['hitpoints'][0] and avg <= entry['hitpoints'][1]:
            defensive_cr = cr_to_num(entry['cr'])
            break

    #   Compute CR Offset from AC.
    cr_from_ac = 0

    for entry in balance_table:
        if monster_data['armor']['class'] == entry['armor_class']:
            cr_from_ac = cr_to_num(entry['cr'])
            break

    # Another place where we're rounding down. I don't know if that's a good
    # thing...
    defensive_cr = defensive_cr - int((defensive_cr - cr_from_ac) / 2)

    # Compute Offensive CR.
    offensive_cr = 0

    #   Compute CR from Average Damage.
    '''
    FIXME[joe] This is a really bad approximation for damage output of a
    monster. This is totalling how much damage all their attack's do and
    dividing by the number of attacks.
    '''
    avg_dpr = 0
    damaging_actions = 0

    for action in monster_data['actions']:
        if action['damage']:
            avg_dpr = max(avg_dpr, average_roll(action['damage']))
            damaging_actions += 1

    avg_dpr = avg_dpr / damaging_actions

    for entry in balance_table:
        avg_dmg = entry['average_damage']

        if avg_dpr >= avg_dmg[0] and avg_dpr <= avg_dmg[1]:
            offensive_cr = cr_to_num(entry['cr'])
            break

    #   Compute CR Offset from Attack Bonus (or save DC).
    attack_bonuses = [ action['to_hit'] for action in monster_data['actions'] ]

    cr_from_attack_bonus = 0
    for entry in balance_table:
        if max(attack_bonuses) == entry['attack_bonus']:
            cr_from_attack_bonus = cr_to_num(entry['cr'])
            break

    offensive_cr = offensive_cr - int((offensive_cr - cr_from_attack_bonus) / 2)

    print("Offensive CR: "+str(offensive_cr))
    print("Defensive CR: "+str(defensive_cr))

    # Compute Average CR. (Round to nearest CR)
    return int((offensive_cr + defensive_cr) / 2)


if __name__ == '__main__':
    monster_block = None

    with open(DATA_DIR+'gargoyle.yaml') as f:
        monster_block = yaml.full_load(f)

    print(monster_block)

    csv_data = csv_to_dict(DATA_DIR+'monster_balancing_table.csv')

    monster_balance_table = parse_monster_balance_table(csv_data)

    print(compute_cr(monster_block, monster_balance_table))
