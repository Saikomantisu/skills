"""Site names: validation and the alliterative adjective-animal generator (e.g. suicidal-squirrel).

Add your own words to either list.
"""

import random
import re

from errors import Fail

ADJECTIVES = """anxious angry awkward bitter broke bored cursed chaotic cranky crusty deranged depressed
dramatic drunk evil edgy feral furious feeble grumpy greasy goofy haunted hungover hostile insane itchy
jaded jittery judgy kinky lazy lonely loud mad moody manic nervous nihilist nosy obsessed petty paranoid
pissed queasy quirky rabid rowdy reckless salty sassy sketchy suicidal sweaty tipsy toxic tired unhinged
unwell vengeful wasted wobbly weird yelling zealous zonked""".split()

ANIMALS = """alpaca axolotl badger beaver bat cobra crab cat donkey duck dingo eel emu ferret frog goose goat
gecko hamster hyena iguana ibis jackal jellyfish koala kiwi llama lemur moose mole narwhal newt octopus
otter possum penguin pigeon quokka raccoon rat sloth squirrel seal toad turtle unicorn vulture walrus
weasel wombat yak zebra""".split()

NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")


def check_name(name):
    if not NAME_RE.match(name):
        raise Fail(f"invalid name '{name}' (lowercase letters, digits, hyphens)")


def random_name(with_number=False):
    animal = random.choice(ANIMALS)
    matches = [a for a in ADJECTIVES if a[0] == animal[0]] or ADJECTIVES
    name = f"{random.choice(matches)}-{animal}"
    return f"{name}-{random.randint(10, 99)}" if with_number else name
