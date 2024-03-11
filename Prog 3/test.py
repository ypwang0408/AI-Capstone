a = set()
a.add(1)
a.add(2)

b = set()
b.add(-2)
b.add(1)
b.add(2)

print(a)
print(b)

all = []
all.append(a)
all.append(b)

c = set()
c.add(1)
c.add(2)

print(c.issubset(a))