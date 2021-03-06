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


class Store:
    """Class in wich the containers are soted"""
    _width: int
    _cash: int
    _containers_list: list

    def __init__(self, width: int):
        """Creates a Store of the given width"""
        
        assert width >= 0
        self._width = width 
        self._cash = 0
        self._containers_list = [[] for i in range(self._width)]
        #we will store the containers in a list of lists where the X axis is indicates
        #the stack where the container is and the Y axis the height the container is.


    def width(self) -> int:
        """Returns the store's width"""
       
        return self._width


    def height(self) -> int:
        """Returns the store's height at that moment"""
       
        height = 0
        for p in self._containers_list:
            if len(p) > height:
                height = len(p)
        return height


    def cash(self) -> int:
        """Returns the store's cash at that moment"""
        
        return self._cash


    def add_cash(self, amount: int) -> None:
        """Given a positive amount of cash, adds it to store's cash"""
        
        assert amount >= 0
        self._cash += amount


    def add(self, c: Container, p: Position) -> None:
        """
        Adds to the list of containers a container c with its position p
        Pre: c must be able to be added to p
        """
        
        assert self.can_add(c, p) #we make sure c can be added to p
        for i in range(c.size):
            self._containers_list[p + i].append(c)
        #We add as many copies as the containers' size in each space it takes up in the list of lists


    def remove(self, c: Container) -> None:
        """
        Deletes from the list of containers the container c
        Pre: c must be removable
        """
        
        assert self.can_remove(c) #we make sure c is removable
        location_cont = self.location(c)[1]
        for i in range(c.size):
            self._containers_list[location_cont + i].remove(c) #aquesta funcio remove es la de les llistes (diferent de self.remove())
        #Com que tenim tantes copies com mida del contenidor, eliminem totes les copies


    def move(self, c: Container, p: Position) -> None:
        """
        Moves a container c to a position p
        Pre: c must be movable
        """
        
        assert self.can_move(c, p) #we make sure c is movable
        self.remove(c)
        self.add(c, p)


    def containers(self) -> List[Container]:
        """Returns the list of the containers that are in the store at that moment"""
        
        cont_lst = []
        for p in self._containers_list:
            for c in p:
                if c not in cont_lst: #we have to make sure that c is not in cont_lst because we added as many copies as the containers' size int the self._containers_list
                    cont_lst.append(c)
        return cont_lst


    def removable_containers(self) -> List[Container]:
        """Returns a list of containers which are removable"""
        
        rem_cont = []
        for p in range(self._width):
            cont = self.top_container(p)
            if cont is not None: #we have to make sure that the position is not empty
                if self.can_remove(cont):
                    if cont not in rem_cont: #if a container is in the top of more than one position (it's size is bigger than one) we only have to add one of it's copies
                        rem_cont.append(cont)
        return rem_cont


    def top_container(self, p: Position) -> Optional[Container]:
        """Returns the container c of the top of a position p if the position is not empty and None if it is"""
        
        if len(self._containers_list[p]) != 0:
            return self._containers_list[p][-1]
        else:
            return None

    #revisar aquesta funcio assert/if/return(-1,-1)
    def location(self, c: Container) -> Location:
        """Returns the location of a container c if it is in the store and (-1, -1) if not"""

        if self.is_in_store(c):
            for p in self._containers_list:
                if c in p:
                    return (p.index(c), self._containers_list.index(p))
                #the first component of the tuple is the position of the continer (in the stack)
                #while the second is the position of the stack (in the list of lists)
        return (-1, -1)


    def can_add(self, c: Container, p: Position) -> bool:
        """Returns if a container c can be added to a position p"""

        height_pila = len(self._containers_list[p])
        #all the heights of the positions that the continer takes up (it's size) 
        #in the right of the position must be the same to be able to add the container
        for i in range(1, c.size):
            if height_pila != len(self._containers_list[p + i]):
                return False
        return True


    def can_remove(self, c: Container) -> bool:
        """
        Returns if a contanier c can be removed from its position
        Pre: c must be in the store
        """

        p = self.location(c)[1] #we are only interested in the X axis (position) of the container
        assert p != -1 #if p == -1 means that c is not in the store
        for i in range(c.size):
            if self.top_container(p + i) != c:
                return False
        return True


    #functions added by myself
    def can_move(self, c: Container, p: Position) -> bool:
        """
        Returns if a container c can be moved to the position p
        Pre: c must be in the store
        """

        return self.can_remove(c) and self.can_add(c, p)


    def is_in_store(self, c: Container) -> bool:
        """Returns if a container c is in the store"""

        for p in self._containers_list:
            if c in p:
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
        stdscr.addstr(maximum + 3, 0, '???' * 2 * self.width())
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
            assert cash == store.cash()

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