import random, sys
from collections import defaultdict

def build(words, n):
    model = defaultdict(list)
    for i in range(len(words) - n):
        model[tuple(words[i:i + n])].append(words[i + n])
    return model

def generate(model, n, length = 50):
    key = random.choices(list(model))
    out = list(key)
    for _ in range(length):
        nxt = random.choice(model.get(tuple(out[-n:]), [None]))
        if nxt is None:
            break
        out.append(nxt)
    return " ".join(out)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    text = open(sys.argv[1]).read().split()
    if len(text) <= n:
        sys.exit(f"File only has {len(text)} words, need more than {n}.")
    print(generate(build(text, n), n))
