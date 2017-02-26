"""
Author: Glen Coppersmith
Email: glen@qntfy.com

Collect some features about the usernames sufficient 
for analysis, but not sufficient enough to make
username recovery significantly easier.
"""
import re
some_swears = """arse
ass
bastard*
bitch*
boob*
butt
cock
crap
cunt*
damn*
dang
darn
dick
dumb*
dyke*
fuck
goddam*
heck
hell
homo
jeez
mofo
motherf*
nigger*
piss*
prick*
pussy*
queer*
screw*
shit*
sob
suck
tit
wanker*
""".replace('*','').split("\n") 

# I somewhat trimmed this list to remove dups and things 
# like 'sonofa' that might mean something slightly 
# different in this context. -- GAC

some_swears = filter(None,some_swears)
contains_swears_ex = re.compile(r"|".join(some_swears))
def name_contains_swear( username ):
    return bool(contains_swears_ex.search(username))
        
mental_health_condition_names = """depress
ptsd
bipolar
anxi
adhd
eatin
anorex
anarex
bulim
bulem
schizo
schitzo
skizo
skitzo
autis
borderline
panic
""".replace('*','').split("\n") 
mental_health_condition_names = filter(None, mental_health_condition_names)
print mental_health_condition_names
contains_mh_ex = re.compile(r"|".join(mental_health_condition_names))
def name_contains_mental_health_condition( username ):
    return bool(contains_mh_ex.search(username))

num_ex = re.compile(r'[0-9]')
char_ex = re.compile(r'[a-zA-Z]')
def name_character_stats(username):
    has_nums = bool(num_ex.search(username))
    has_chars = bool(char_ex.search(username))
    has_underscore = '_' in username
    return {'has_digits':has_nums, 
            'has_chars':has_chars,
            'has_underscore':has_underscore}

def calc_username_statistics( username ):
    """
    Takes a `username`
    Returns booleans about what the username is made of
    [ Does it contain a swear word,
    Does it contain a mental health condition name,
    Does it have at least one number in it,
    Does it have at least one character in it,
    Does it have at least one underscore in it]
    """
    contains_swear = name_contains_swear( username )
    contains_mental_health_condition = name_contains_mental_health_condition( username )
    character_stats = name_character_stats(username)
    #print username, contains_swear, contains_mental_health_condition, character_stats
    stats = {'contains_swear':contains_swear, 
            'contains_mental_health_condition':contains_mental_health_condition}
    for k,v in character_stats.items():
        stats[k]=v
    return stats
        
if __name__ == '__main__':
    """Run this standalone to test functionality out"""
    for u in ['GlenCoppersmith','fuck_this','bipolar_that','this_shit','that_bipolar','that_bipolar444']:
        print u, calc_username_statistics(u)


    
