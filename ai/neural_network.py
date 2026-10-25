import math, random

random.seed(1)

def sig(x): return 1 / (1 + math.exp(-x))

# 2 inputs -> 3 hidden -> 1 output
H = 3
w1 = [[random.uniform(-1, 1) for _ in range(2)] for _ in range(H)]
b1 = [0.0] * H
w2 = [random.uniform(-1, 1) for _ in range(H)]
b2 = 0.0

data = [([0, 0], 0), ([0, 1], 1), ([1, 0], 1), ([1, 1], 0)]
lr = 0.5

def forward(x):
    h = [sig(sum(w1[j][i] * x[i] for i in range(2)) + b1[j]) for j in range(H)]
    o = sig(sum(w2[j] * h[j] for j in range(H)) + b2)
    return h, o

for epoch in range(10001):
    loss = 0
    for x, y in data:
        h, o = forward(x)
        loss += (o - y) ** 2

        # backdrop
        d_o = (o - y) * o * (1 - o)
        d_h = [d_o * w2[j] * h[j] * (1 - h[j]) for j in range(H)]

        for j in range(H):
            w2[j] -= lr * d_o * h[j]
            b1[j] -= lr * d_h[j]
            for i in range(2):
                w1[j][i] -= lr * d_h[j] * x[i]
        b2 -= lr * d_o

    if epoch % 2000 == 0:
        print(f"epoch {epoch:5d} loss {loss:.5f}")

print()
for x, _ in data:
    h, _ = forward(x)
    print(x, [round(v, 2) for v in h])
    print(x, "->", round(forward(x)[1], 3), f"(target{y})")
