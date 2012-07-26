from collections import OrderedDict
from string import ascii_lowercase as alphabet
import unicodedata

from abilities import abilities
from common import types
from items import items
from locations import kingdoms
from pokemon import pokemon
from warriors import warriors, warrior_skills

singlename_to_tablename =  {
    'ability': 'abilities',
    'kingdom': 'conquest_kingdoms',
    'required_stat': 'stats',
    'skill': 'conquest_warrior_skills',
    'warrior': 'conquest_warriors',
}

def identifier(name):
    """Create a valid identifier from a name."""

    name = name.lower()
    name = name.replace(' ', '-')
    name = name.replace('&', 'and')

    # Strip macrons and misc punctuation
    name = ''.join(char for char in unicodedata.normalize('NFD', name)
                   if char in alphabet or char == '-')

    return name

def insert(table, columns, values):
    values = ', '.join(format_value(column, value)
                       for column, value in zip(columns, values))
    columns = ', '.join(columns)

    return 'insert into {0} ({1}) values ({2});'.format(table, columns, values)

def format_value(column, value):
    if isinstance(value, int):
        # This covers booleans too
        return str(value)
    elif isinstance(value, str):
        value = "E'{0}'".format(value.replace("'", r"\'"))
        if column.endswith('_id'):
           foreign_table = column[:-3]
           foreign_table = singlename_to_tablename.setdefault(foreign_table,
             '{0}s'.format(foreign_table))
           value = '(select id from {0} where identifier={1})'.format(
             foreign_table, value)
        return value
    else:
        raise TypeError('Unknown thing for SQL insert: {0!r}'.format(value))

def do_abilities():
    # Some (but only some) abilities exist in the main series, so we need to
    # figure that out.
    print('create temp table abilitemp ( identifier text, name text );')
    for ability in abilities:
        if ability.name.startswith('dummy'):
            continue

        print(insert('abilitemp', ['identifier', 'name'],
                     [identifier(ability.name), ability.name]))

    print('alter sequence abilities_id_seq restart with 10001;')

    print('insert into abilities (identifier, generation_id) '
          'select identifier, 5 from abilitemp '
          'where identifier not in (select identifier from abilities);')

    print('insert into ability_names (ability_id, local_language_id, name) '
          'select (select id from abilities where abilities.identifier='
          'abilitemp.identifier), 9, name from abilitemp where name not in'
          '(select name from ability_names where local_language_id=9);')

def do_kingdoms():
    columns = ['id', 'identifier', 'type_id']

    for n, kingdom in enumerate(kingdoms):
        print(insert(
            'conquest_kingdoms',
            ['id', 'identifier', 'type_id'],
            [n + 1, identifier(kingdom.name), types[n]]
        ))

        print(insert(
            'conquest_kingdom_names',
            ['kingdom_id', 'local_language_id', 'name'],
            [identifier(kingdom.name), 9, kingdom.name]
        ))

def do_max_links():
    # This table is enormous; this way makes things much quicker with Postgres
    print('copy conquest_max_links (warrior_rank_id, pokemon_species_id,'
          'max_link) from stdin;')

    for n, warrior in enumerate(warriors[:242]):
        for pokemon, link in warrior.max_links.items():
            print('{0}\t{1}\t{2}'.format(n + 1, pokemon.national_id, link))

    print(r'\.')

def do_pokemon():
    for gallery_id, single_pokemon in enumerate(pokemon):
        gallery_id += 1

        for n, ability in enumerate(single_pokemon.abilities):
            print(insert(
                'conquest_pokemon_abilities',
                ['pokemon_species_id', 'ability_id', 'slot'],
                [single_pokemon.national_id, identifier(ability.name), n + 1]
            ))

       for stat in ('hp', 'attack', 'defense', 'speed'):
           print(insert(
               'conquest_pokemon_stats',
               ['pokemon_species_id', 'stat_id', 'stat'],
               [single_pokemon.national_id, stat, getattr(single_pokemon, stat)]
           ))

       template = 'update pokemon_species set {{0}}={{1}} where id={0};'.format(
           single_pokemon.national_id)

       print(template.format('conquest_range', single_pokemon.range))
       print(template.format('conquest_gallery_order', gallery_id))
       print(template.format('conquest_move_id', '(select id from moves '
         'where identifier={0})'.format(single_pokemon.move.name))

def do_pokemon_evolution():
    stats = ('hp', 'attack', 'defense', 'speed')

    for single_pokemon in pokemon:
        evo_conditions = [
          (single_pokemon.evo_condition_1, single_pokemon.evo_parameter_1),
          (single_pokemon.evo_condition_2, single_pokemon.evo_parameter_2)
        ]

        info = OrderedDict()

        for condition, parameter in evo_conditions:
            if condition is None:
                pass
            elif 0b0000 <= condition <= 0b0011:
                info['required_stat_id'] = stats[condition]
                info['minimum_stat'] = parameter
            elif condition == 0b0100:
                info['minimum_link'] = parameter
            elif condition == 0b0101:
                info['kingdom_id'] = parameter
            elif condition == 0b0110:
                info['warrior_gender_id'] = ('male', 'female')[parameter]
            elif condition == 0b0111:
                info['item_id'] = identifier(items[parameter].name)
            elif condition == 0b1000:
                info['recruiting_ko_required'] = True

        if not info:
            # No conditions; nothing evolves into this Pokémon
            continue

        info['evolved_species_id'] = single_pokemon.national_id

        print(insert('conquest_pokemon_evolution', info.keys(), info.values()))

def do_warriors():
    new_warrior = True

    # After the 242 actual warrior structs come some NPCs; we don't want those
    for n, warrior in enumerate(warriors[:242]):
        if warrior.name == 'Player':
            warrior.name = 'Player ({0})'.format(warrior.gender)
        warrior.identifier = identifier(warrior.name)

        if new_warrior:
            rank = 1
            print(insert(
                'conquest_warriors',
                ['identifier', 'gender_id'],
                [warrior.identifier, warrior.gender]
            ))

            print(insert(
                'conquest_warrior_names',
                ['warrior_id', 'local_language_id', 'name'],
                [warrior.identifier, 9, warrior.name]
            ))

            for n, type_ in enumerate(warrior.types):
                print(insert(
                    'conquest_warrior_specialties',
                    ['warrior_id', 'type_id', 'slot'],
                    [warrior.identifier, type_, n + 1]
                ))
        else:
            rank += 1

        print(insert(
            'conquest_warrior_ranks',
            ['warrior_id', 'rank', 'skill_id', 'capacity'],
            [warrior.identifier, rank, identifier(warrior.skill.name),
             warrior.capacity]
        ))

        new_warrior = warrior.next_rank == 252

def do_warrior_skills():
    for n, skill in enumerate(warrior_skills):
        if skill.name.startswith('dummy'):
            break

        print(insert(
            'conquest_warrior_skills',
            ['identifier'],
            [identifier(skill.name)]
        ))

        print(insert(
            'conquest_warrior_skill_names',
            ['skill_id', 'local_language_id', 'name'],
            [identifier(skill.name), 9, skill.name]
        ))


print('begin;')

# These are called in table dependency order
#do_kingdoms()
#do_pokemon_evolution()
#do_warrior_skills()
#do_warriors()
#do_abilities()
do_pokemon()
#do_max_links()

print('commit;')
