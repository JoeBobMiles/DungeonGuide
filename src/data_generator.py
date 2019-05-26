"""
@file data_generator.py
@author Joseph Miles <josephmiles2015@gmail.com>
@date 2019-05-22

Retrieves monster information from orcpub.com and generates YAML stat-blocks.
"""

import re
import requests
from lxml import html

orcpub = "http://www.orcpub.com"

# Retreive monster registry.
page = requests.get(orcpub + "/dungeons-and-dragons/5th-edition/monsters")
# Transform monster registry page into a DOM tree.
tree = html.fromstring(page.content)

# Retreive all the monster names (the first element of this list is actually a
# component of the page's title section).
names = tree.xpath('//strong[@itemprop="name"]/text()')[1:]
# Retreive the links to visit for each monster.
links = tree.xpath('//div[@class="lv-body"]/div/a/@href')

monster_proto_list = []

# Pair monster name and link.
for i in range(0, max(len(names), len(links))):
    monster_proto_list.append(( names[i] or "", links[i] or "" ))

# For each monster name and link pair, scrape data and export it to a YAML file.
for name, link in monster_proto_list:
    print("Getting stats for {0}".format(name))

    monster_data = {}
    monster_data['name'] = name

    page = requests.get(orcpub + link)
    tree = html.fromstring(page.content)

    # Retreive monster size, type, and alignment.
    details = tree.xpath('//div[@class="char-details-section"]/em/text()')

    monster_data['size'] = details[0].lower()
    monster_data['type'] = details[1].lower()

    # NOTE[joe] This could be done with a list comprehension.
    # But I'm particular and don't want to write a list comprehension that is
    # over the column count.
    monster_data['alignment'] = []
    for i, s in enumerate(details[3].split()):
        if s.lower() != "alignment":
            monster_data['alignment'].append(s.lower())

    # Retreive monster armor class.
    monster_data['armor'] = int(tree.xpath(
        '//div[@class="char-details-section" and position() = 2]'+
        '/div[@class="char-details-field" and position() = 1]/span/text()')[0])

    # Retreive monster hit dice.
    monster_data['hitpoints'] = tree.xpath(
        '//div[@class="char-details-section" and position() = 2]'+
        '/div[@class="char-details-field" and position() = 2]/span/span/span/'+
        'text()')

    monster_data['hitpoints'] = re.match(
        r"\d+\((.*)\)", "".join(monster_data['hitpoints'])).group(1)

    monster_data['hitpoints'] = "".join(monster_data['hitpoints'].split())

    # Retreive monster speeds.
    monster_data['speed'] = tree.xpath(
        '//div[@class="char-details-section" and position() = 2]'+
        '/div[@class="char-details-field" and position() = 3]/span/text()')[0]

    monster_data['speed'] = "".join(re.split(r" \(.*\)",
                                             monster_data['speed']))
    monster_data['speed'] = re.split(r" ft\.,?",
                                     monster_data['speed'])

    monster_data['speed'] = [ s for s in monster_data['speed'] if s != '' ]

    temp = []
    for i, s in enumerate(monster_data['speed']):
        parts = monster_data['speed'][i].split()

        if len(parts) == 1:
            temp.append(('land', int(parts[0])))

        else:
            parts[1] = int(parts[1])
            parts = tuple(parts)
            temp.append(parts)

    monster_data['speed'] = dict(temp)

    # Retreive monster stats.
    monster_data['stats'] = tree.xpath(
        '//div[@class="char-details-section" and position() = 3]'+
        '/table/tbody/tr/td/div/text()')

    stat_names = [ "str", "dex", "con", "int", "wis", "chr" ]
    stats = []
    for i, s in enumerate(monster_data['stats']):
        stat = int(re.match(r"(\d{1,2}).*", s).groups()[0])
        stats.append((stat_names[i], stat))

    monster_data['stats'] = dict(stats)

    # Retreive monster proficiency bonus.
    monster_data['proficiency'] = int(float(tree.xpath(
        '//div[@class="char-details-section" and position() = 4]'+
        '/div[@class="char-details-field" and position() = 1]/span/text()')[0]))

    # Retreive monster saving throws (if any).
    monster_data['saves'] = tree.xpath(
        '//h5[text() = "Saving Throws"]/../span/text()')

    if monster_data['saves']:
        monster_data['saves'] = re.split(r", ", monster_data['saves'][0])

        for i, s in enumerate(monster_data['saves']):
            s = s.split()
            monster_data['saves'][i] = (s[0].lower(), int(s[1]))

        monster_data['saves'] = dict(monster_data['saves'])

    monster_data['immunities'] = {}

    # Retreive monster condition immunities (if any).
    monster_data['immunities']['condition'] = tree.xpath(
        '//h5[text() = "Condition Immunities"]/../span/text()')

    if monster_data['immunities']['condition']:
        monster_data['immunities']['condition'] = re.split(
            r", ", monster_data['immunities']['condition'][0])

    # Retreive monster damage immunties (if any).
    monster_data['immunities']['damage'] = tree.xpath(
        '//h5[text() = "Damage Immunities"]/../span/text()')

    if monster_data['immunities']['damage']:
        _ = re.split(r"; ", monster_data['immunities']['damage'][0])

        immunities = re.split(r", ", _[0])

        if len(_) == 2:
            immunities.append(_[1])

        monster_data['immunities']['damage'] = immunities

    # Retreive monster damage resistances (if any).
    monster_data['resistances'] = {}

    monster_data['resistances']['damage'] = tree.xpath(
        '//h5[text() = "Damage Resistances"]/../span/text()')

    if monster_data['resistances']['damage']:
        _ = re.split(r"; ", monster_data['resistances']['damage'][0])

        resistances = re.split(r", ", _[0])

        if len(_) == 2:
            resistances.append(_[1])

        monster_data['resistances']['damage'] = resistances

    # TODO[joe] Retreive monster damage vulnerabilities (if any).
    # I don't think OrcPub lists vulnerabilities, which is a problem.

    # Retreive monster skills (if any).
    monster_data['skills'] = tree.xpath(
        '//h5[text() = "Skills"]/../span/text()')

    if monster_data['skills']:
        monster_data['skills'] = re.split(r", ", monster_data['skills'][0])

        for i, s in enumerate(monster_data['skills']):
            s = s.split()
            monster_data['skills'][i] = (" ".join(s[:len(s)-1]).lower(),
                                         int(s[-1]))

        monster_data['skills'] = dict(monster_data['skills'])

    # Retreive monster senses (if any) and passive perception.
    senses = tree.xpath('//h5[text() = "Senses"]/../span/text()')

    if senses:
        senses = "".join(re.split(r" \(.*\)", senses[0]))
        senses = re.split(r" ?ft\.,? ?", senses)

        # NOTE[joe] We select the last item of the split string because passive
        # perception is listed as "passive Perception #".
        monster_data['passive perception'] = int(senses[-1].split()[-1])

        if len(senses) > 1:
            senses = senses[:len(senses)-1]

            _ = []

            for i, sense in enumerate(senses):
                sense = sense.split()
                _.append((sense[0].lower(), int(sense[1])))

            # Sort out entries that start with conjunctions.
            # NOTE[joe] This is to overcome issues with "uncommon" phrasings
            # of the senses section. (See the Grimlock stat-block for an
            # example of this.)
            _ = [ t for t in _ if t[0] not in ['and', 'or'] ]

            monster_data['senses'] = dict(_)

        else:
            monster_data['senses'] = {}

    # TODO[joe] Retreive monster languages.

    # Retreive monster challenge rating (CR).
    monster_data['challenge'] = tree.xpath(
        '//h5[text() = "Challenge"]/../span/span/span/text()')[0]

    monster_data['abilities'] = tree.xpath(
        '//div[@class="char-details-section"]/../div/p/em/strong/text()')


    if monster_data['abilities']:
        descriptions = tree.xpath(
            '//strong[text() = "{0}"]/../../../p/span/text()'.format(
                monster_data['abilities'][0]))

        for i, ability in enumerate(monster_data['abilities']):
            ability_data = {}

            # Trim off the trailing period and drop to lowercase.
            ability_data['name'] = ability[:len(ability)-1].lower()
            ability_data['text'] = descriptions[i]

            # TODO[joe] Extract damage info from abilities.
            # This is going to take a lot of work to do.
            # TODO[joe] Retreive monster spell casting ability (if any).
            # This is somewhat easier to do, but will be involved when it comes
            # to reading spell descriptions. USE NLTK TO DO THIS!

            monster_data['abilities'][i] = ability_data

    # Retreive monster multi-attack combos (if any).
    # TODO[joe] Read multiattack text to figure out what kind of multiattacks
    # the creature has.
    monster_data['multiattack'] = tree.xpath(
        '//strong[text() = "Multiattack."]/../../span/text()')

    # Retreive monster actions.
    actions = tree.xpath('//h4[text() = "Actions"]/../p/em/strong/text()')
    descriptions = tree.xpath('//h4[text() = "Actions"]/../p/span/text()')

    monster_data['actions'] = {}

    if actions:
        if actions[0] == "Multiattack.":
            actions = actions[1:]
            descriptions = descriptions[1:]

        # TODO[joe] Parse action text to figure out what it does.
        for i, action in enumerate(actions):
            action = action[:len(action)-1].lower().strip()
            monster_data['actions'][action] = descriptions[i]

    # Retreive monster reactions (if any).
    reactions = tree.xpath('//h4[text() = "Reactions"]/../p/em/strong/text()')
    descriptions = tree.xpath('//h4[text() = "Reactions"]/../p/span/text()')

    monster_data['reactions'] = {}

    if reactions:
        # TODO[joe] Parse reaction text to figure out what it does.
        for i, reaction in enumerate(reactions):
            reaction = reaction[:len(reaction)-1].lower().strip()
            monster_data['reactions'][reaction] = descriptions[i]

    # Retreive monster legendary actions (if any).
    legendary_actions = tree.xpath(
        '//h4[text() = "Legendary Actions"]/../p/em/strong/text()')
    descriptions = tree.xpath(
        '//h4[text() = "Legendary Actions"]/../p/span/text()')

    monster_data['legendary actions'] = {}

    if legendary_actions:
        # TODO[joe] Parse legendary text to figure out what it does.
        for i, action in enumerate(legendary_actions):
            action = action[:len(action)-1].lower().strip()
            monster_data['legendary actions'][action] = descriptions[i]

    print(monster_data)

    # break
