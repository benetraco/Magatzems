"""
Template file for store.py module.
"""

from dataclasses import dataclass
from turtle import width
from typing import Optional, TextIO, List, Tuple
import curses
import time


TimeStamp = int


Position = int


Location = Tuple[int, int]
# a la Tuple  hi va primer l'eix Y (altura - fila) i despres l'eix X (pila - columna)


@dataclass
class TimeRange:
    start: TimeStamp
    end: TimeStamp


@dataclass
class Container:
    identifier: int
    size: int
    value: int
    arrival: TimeRange
    delivery: TimeRange

#funcions que es poden afegir: def caducat(self, c: Container) -> bool:
class Store:
    """Class in wich the containers are soted"""

    def __init__(self, width: int):
        """Creates a Store of the given width"""
        
        assert width >= 0
        self._width = width 
        self._cash = 0
        self._containers_list: list  = [[] for i in range(self._width)]
        #els containers els emmagatzerem amb una llista de llistes on l'eix de les x indicarà 
        #la pila en que es troba el contenidor i el de les y indicarà l'altura a la que es troba.


    def width(self) -> int:
        """Returns the store's width"""
       
        return self._width


    def height(self) -> int:
        """Returns the store's height at that moment"""
       
        height = 0
        for stack in self._containers_list:
            if len(stack) > height:
                height = len(stack)
        return height


    def cash(self) -> int:
        """Returns the store's cash at that moment"""
        
        return self._cash


    def add_cash(self, amount: int) -> None:
        """Given a positive amount of cash, adds it to store's cash"""
        
        assert amount >= 0
        self._cash += amount


    def add(self, c: Container, p: Position) -> None:
        """Adds to the list of containers a container c with its position p"""
        
        assert self.can_add(c, p)
        for i in range(c.size):
            self._containers_list[p + i].append(c)
        #Afegim tantes copies com mida del contenidor a cada espai que ocupa dins la llista de llistes


    def remove(self, c: Container) -> None:
        """Deletes from the list of containers the container c if it's possible"""
        
        assert self.can_remove(c)
        location_cont = self.location(c)[1]
        for i in range(c.size):
            self._containers_list[location_cont + i].remove(c) #aquesta funcio remove es la de les llistes (diferent de self.remove())
        #Com que tenim tantes copies com mida del contenidor, eliminem totes les copies


    def move(self, c: Container, p: Position) -> None:
        """Moves a container c to a position p if it's possible"""
        
        assert self.can_remove(c)
        self.remove(c)
        assert self.can_add(c, p)
        self.add(c, p)


    def containers(self) -> List[Container]:
        """Returns the list of containers that are in the store at that moment"""
        
        containers_list = []
        for stack in self._containers_list:
            for c in stack:
                if c not in containers_list:
                    containers_list.append(c)
        return containers_list


    def removable_containers(self) -> List[Container]:
        """Returns a list of containers which are removable"""
        
        rem_cont = []
        for i in range(self._width):
            cont = self.top_container(i)
            if cont is not None: #comprovem que a la pila hi ha algun container
                if self.can_remove(cont):
                    if cont not in rem_cont: #si un container esta a sobra de mes de una pila, nomes afegim una copia seva
                        rem_cont.append(cont)
        return rem_cont


    def top_container(self, p: Position) -> Optional[Container]:
        """Returns the container of the top of a position p if the position is not empty"""
        
        if len(self._containers_list[p]) != 0:
            return self._containers_list[p][-1]
        else:
            return None

    #revisar aquesta funcio assert/if/return(-1,-1)
    def location(self, c: Container) -> Location:
        """Returns the location of a container"""

        assert self.is_in_store(c)
        for stack in self._containers_list:
            if c in stack:
                return (stack.index(c), self._containers_list.index(stack))
                #el primer component de la tupla es la posicio del container (dins la pila)
                #mentre que la segona es la posicio de la pila (dins la llista de llistes)
        return (-1, -1) #returns -1, -1 if c is not in the store


    def can_add(self, c: Container, p: Position) -> bool:
        """Returns if a container c can be added to a position p"""

        height_pila = len(self._containers_list[p])
        #totes les altures de les piles que hi ha fins a la mida del contenidor a la dreta 
        #han de ser iguals per poder afegir el contenidor
        for i in range(1, c.size):
            if height_pila != len(self._containers_list[p + i]):
                return False
        return True


    def can_remove(self, c: Container) -> bool:
        """Returns if a contanier c can be removed from its position"""

        assert self.is_in_store(c)
        location_cont = self.location(c)[1] #només ens interessa l'eix X (pila) on es troba
        for i in range(c.size):
            if self._containers_list[location_cont + i][-1] != c:
                return False
        return True

    #funcions fetes per mi
    def is_in_store(self, c: Container) -> bool:
        """Returns if a container c is in the store"""

        for stack in self._containers_list:
            if c in stack:
                return True
        return False
    
    def empty(self) -> bool:
        """Returns if the store is empty"""

        return self._containers_list == [[] for i in range(self._width)]


    def write(self, stdscr: curses.window, caption: str = ''):

        maximum = 15  # maximum number of rows to write
        delay = 0.05  # delay after writing the state

        # start: clear screen
        stdscr.clear()

        # write caption
        stdscr.addstr(0, 0, caption)
        # write floor
        stdscr.addstr(maximum + 3, 0, '—' * 2 * self.width())
        # write cash
        stdscr.addstr(maximum + 4, 0, '$: ' + str(self.cash()))

        # write containers
        for c in self.containers():
            row, column = self.location(c)
            if row < maximum:
                p = 1 + c.identifier * 764351 % 250  # some random color depending on the identifier of the container
                stdscr.addstr(maximum - row + 2, 2 * column, '  ' * c.size, curses.color_pair(p))
                stdscr.addstr(maximum - row + 2, 2 * column,
                              str(c.identifier % 100), curses.color_pair(p))

        # done
        stdscr.refresh()
        time.sleep(delay)


class Logger:

    """Class to log store actions to a file."""

    _file: TextIO

    def __init__(self, path: str, name: str, width: int):
        self._file = open(path, 'w')
        print(0, 'START', name, width, file=self._file)

    def add(self, t: TimeStamp, c: Container, p: Position):
        print(t, 'ADD', c.identifier, p, file=self._file)

    def remove(self, t: TimeStamp, c: Container):
        print(t, 'REMOVE', c.identifier, file=self._file)

    def move(self, t: TimeStamp, c: Container, p: Position):
        print(t, 'MOVE', c.identifier, p, file=self._file)

    def cash(self, t: TimeStamp, cash: int):
        print(t, 'CASH', cash, file=self._file)


def read_containers(path: str) -> List[Container]:
    """Returns a list of containers read from a file at path."""

    with open(path, 'r') as file:
        containers: List[Container] = []
        for line in file:
            identifier, size, value, arrival_start, arrival_end, delivery_start, delivery_end = map(
                int, line.split())
            container = Container(identifier, size, value, TimeRange(
                arrival_start, arrival_end), TimeRange(delivery_start, delivery_end))
            containers.append(container)
        return containers


def check_and_show(containers_path: str, log_path: str, stdscr: Optional[curses.window] = None):
    """
    Check that the actions stored in the log at log_path with the containers at containers_path are legal.
    Raise an exception if not.
    In the case that stdscr is not None, the store is written after each action.
    """

    # get the data
    containers_list = read_containers(containers_path)
    containers_map = {c.identifier: c for c in containers_list}
    log = open(log_path, 'r')
    lines = log.readlines()

    # process first line
    tokens = lines[0].split()
    assert len(tokens) == 4
    assert tokens[0] == "0"
    assert tokens[1] == "START"
    name = tokens[2]
    width = int(tokens[3])
    last = 0
    store = Store(width)
    if stdscr:
        store.write(stdscr)

    # process remaining lines
    for line in lines[1:]:
        tokens = line.split()
        time = int(tokens[0])
        what = tokens[1]
        assert time >= last
        last = time

        if what == "CASH":
            cash = int(tokens[2])
            #assert cash == store.cash()

        elif what == "ADD":
            identifier, position = int(tokens[2]), int(tokens[3])
            store.add(containers_map[identifier], position)

        elif what == "REMOVE":
            identifier = int(tokens[2])
            container = containers_map[identifier]
            store.remove(container)
            if container.delivery.start <= time < container.delivery.end:
                store.add_cash(container.value)

        elif what == "MOVE":
            identifier, position = int(tokens[2]), int(tokens[3])
            store.move(containers_map[identifier], position)

        else:
            assert False

        if stdscr:
            store.write(stdscr, f'{name} t: {time}')