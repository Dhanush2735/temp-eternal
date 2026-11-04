import io

readme = 'worldfill/README.md'
s = io.open(readme, encoding='utf-8').read()
needle = '**Limits**: the grid is a design'
i = s.find(needle)
assert i > 0, 'anchor missing'
j = s.find('\n\n', i)
assert j > i
add = '''

**Part 3, F1, the ways priced and gated.** `timeline/Agency.java`, Minecraft-free. Part 2 said what a
change costs and not whether the player can do it at all, so each of the ten ways is now judged against
a **`Situation`** of five things and no more: how many people are within reach (from the town pack's own
counts), the player's standing (outsider, resident, notable, officer, ruler), how many follow them,
whether there is a workshop, and what is in the purse. There are **three answers**, because a bare no is
useless in a world: **yes** with the count and the cost, **not yet** with what is missing (*"a stranger
cannot do this here; it wants a resident, known by name"*), and **no** with the arithmetic (*"this needs
about 1000 people within reach and a village has 200"*). Reasons that cannot be argued with are checked
first, so a player in an empty valley is not told to go and collect fifty followers.

**The refusal list is read, not copied.** `Agency` uses `InWorldInterventionDetector.STOPPABLE_KINDS`
and `REFUSED_KINDS` directly and the probe asserts the sets are equal, so there is one list of what a
person may interrupt. A kind on neither list is a no: an unlisted kind is not a permission.

**The measured ordering, and it contradicted the plan.** Fed real town counts, a **stranger** can touch
a person and tell the future, and nothing else, at Cahokia 1100 (20,000), Tenochtitlan 1500 (212,500),
Rome -150 (300,000), Kolkata 1710 (12,000) and London 1801 (1,011,157). A **resident** holds the same
four ways in every one of them. **So the size of a place decides almost nothing**: once a town is big
enough to have a market, who you are and what you bring decides everything, and only a hamlet under a
thousand people is genuinely narrowed by its count. The crown is a **standing** requirement and not a
size one, which is the opposite of what this part expected to find.

Two bugs, both in the probe: the town pack carries **twelve** fields and its own header lists eleven, so
the reader stopped at town 131; and "nearest town" is the wrong question, because nearest to Tenochtitlan
in 1500 is *Greater Mexico City*, a modern metro area with no count that year, which read as an empty
city. It now takes the largest count within a degree, falling back to nearest only when nothing there is
counted. One rule was corrected against the code: a stranger cannot marry, because a marriage needs two
people and one of them has to know you.

**Limits**: the thresholds are judgements in one table (twenty people for a town, fifty behind you for a
war, a hundred for a crown, a thousand for a war to exist at all); **standing is not yet a thing in the
world**, so today every player is an outsider and four ways are permanently out of reach until part 4
makes roles; followers and the purse are not wired to anything; and no data pack, because the situations
are computed from packs that already ship.'''
s = s[:j] + add + s[j:]
io.open(readme, 'w', encoding='utf-8').write(s)
print('readme ok')

p = 'PROGRESS.md'
s = io.open(p, encoding='utf-8').read()
old_head = "| **The step in progress (48) - parts** | **2** | **7** | survey and the change record (turn 198); next is F1's ways, priced |"
assert old_head in s
s = s.replace(old_head, "| **The step in progress (48) - parts** | **3** | **7** | survey, change record, ways priced and gated (turn 198); next is F5, player roles |")
s = s.replace("In progress: part 2 of 7 (turn 198)", "In progress: part 3 of 7 (turn 198)")
i = s.find('| 48 |')
assert i > 0
j = s.find('\n', i)
add2 = (" **Part 3, F1 priced and gated.** `timeline/Agency.java`: each of the ten ways judged against a "
        "`Situation` of five things (people within reach from the town pack's own counts, standing, "
        "followers, a workshop, a purse), with three answers - yes, **not yet** naming what is missing, "
        "and **no** giving the arithmetic - and the non-negotiable reasons checked first. The refusal "
        "list is **read from `InWorldInterventionDetector` rather than copied**, and the probe asserts "
        "the two sets are equal, so there is one list of what a person may interrupt; a kind on neither "
        "list is a no. **Fed real counts, the measurement contradicted the plan**: a stranger can touch "
        "a person and tell the future and nothing else at Cahokia 1100 (20,000 people), Tenochtitlan "
        "1500 (212,500), Rome -150 (300,000), Kolkata 1710 (12,000) and London 1801 (1,011,157), and a "
        "resident holds the same four ways in all five, so **the size of a place decides almost "
        "nothing** once it can hold a market: standing and what the player brings decide everything, "
        "and only a hamlet under a thousand is narrowed by its count. The crown is a standing "
        "requirement, not a size one. Two bugs, both in the probe: the town pack carries twelve fields "
        "and its header lists eleven (the reader stopped at town 131), and nearest-town is the wrong "
        "question because nearest to Tenochtitlan in 1500 is Greater Mexico City with no count that "
        "year. 81 checks. Limits: the thresholds are judgements, standing is not yet a thing in the "
        "world so every player is an outsider today, and the purse and followers are not wired.")
s = s[:j] + add2 + s[j:]
io.open(p, 'w', encoding='utf-8').write(s)
i = s.find('| 48 |')
print('pipes', s[i:s.find('\n', i)].count('|'))
