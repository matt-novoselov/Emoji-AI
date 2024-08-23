import random

# Load word lists
with open("app/Username_Generator/nouns.txt", 'r') as infile:
    nouns = infile.read().strip(' \n').split('\n')
with open("app/Username_Generator/adjectives.txt", 'r') as infile:
    adjectives = infile.read().strip(' \n').split('\n')


# Generate usernames
async def GenerateUsername():
    # construct username
    word1 = random.choice(adjectives)
    word2 = random.choice(nouns)
    word1 = word1.title()
    word2 = word2.title()
    username = '{}{}'.format(word1, word2)

    return username.replace("-", "")
