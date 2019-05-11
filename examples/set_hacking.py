from itertools import combinations

def make_combo(_max, _pick):
  comb = combinations(list(range(1,_max+1)), _pick)
  return list(comb)

print(make_combo(3, 2))

def make_next(_max, _pick):
  full_combo = [a for a in make_combo(_max, _pick)]
  sub_combo = [b for b in full_combo if _max in b]
  return sub_combo

top = 13
maximum_pick = []
max_length = 0
for _max in range(top):
  for picks in range(top):
    working_list = make_next(_max, picks)
    length = len(working_list)
    print(_max, picks, length, working_list)
    if max_length < length:
      maximum_pick = [_max, picks]
      max_length = length

print(maximum_pick, max_length)
