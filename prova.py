from store import *

def show(S: Store):
    list = S._containers_list
    for pila in list:
        for c in pila:
            print("*", end='')
        print()
    print("----------")


S = Store(10)
c1 = Container(1,1,1,0,0)
c2 = Container(2,2,2,0,0)
c3 = Container(3,3,3,0,0)
c4 = Container(4,4,4,0,0)
S.add(c3, 1)
S.add(c2, 1)
S.add(c4, 5)
S.add(c1, 5)
show(S)
print(S.removable_containers())