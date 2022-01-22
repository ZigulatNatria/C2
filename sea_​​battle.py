from random import randint
import time

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):   #сравнение точек
        return self.x == other.x and self.y == other.y

    def __repr__(self):    #список точек
        return f"Dot({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, deck, sn): #объявление носа, количества палуб и север-юг (положения коробля по X, Y)
        self.bow = bow
        self.deck = deck
        self.sn = sn
        self.lives = deck

    @property
    def ship_coordinates(self):
        ship_list = [] #список точек корабля
        for i in range(self.deck):
            coor_x = self.bow.x
            coor_y = self.bow.y

            if self.sn == 0:  #если север-юг равет 0, то корабль ориентирован по оси Х
                coor_x += i

            elif self.sn == 1: #если север-юг равен 1, то корабль ориентирован по оси Y
                coor_y += i

            ship_list.append(Dot(coor_x, coor_y)) #добавляеем точки корабля

        return ship_list

    def fire(self, shot):
        return shot in self.ship_coordinates #проверека является ли точка в которую выстрелили частью корабля и команды )))


class GameField:
    def __init__(self, hide = False, size = 6): #параметр для скрытия поля, размер поля
        self.hide = hide
        self.size = size

        self.count = 0
        self.anticount = 7 #для подсчёта кораблей

        self.field = [['0'] * size for z in range(size)] #посторение сетки поля
        self.busy = [] #список занятых чем либо клеток
        self.squadron = [] #эскадра кораблей

    def __str__(self):
        cor = ''
        cor += '  | 1 | 2 | 3 | 4 | 5 | 6 |'  #обозначение координат

        for i, row in enumerate(self.field):
            cor += f'\n{i+1} | ' + ' | ' .join(row) + ' | ' #постоение сетки поля

        if self.hide:
            cor = cor.replace('■', 'O')  #скрывание точки

        return cor

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size)) #проверка нахождения точки в поле доски

    def add_ship(self, ship): #добавление корабля на поле

        for d in ship.ship_coordinates:
            if self.out(d) or d in self.busy: #проверка подходящей точки (не за границы поля) и не на занятую клетку
                raise BoardWrongShipException() #исключение при попадании на не подходящую точку

        for d in ship.ship_coordinates:
            self.field[d.x][d.y] = '■' #добавление точки на игровое поле символом ■
            self.busy.append(d)      #добавление точки в список занятых

        self.squadron.append(ship) #добавление корабля в эскадру
        self.environment(ship) #для определения окружения

    def environment(self, ship, verb=False): #определение точек окружения (точки занятые вокруг корабля)
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.ship_coordinates:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "•"
                    self.busy.append(cur)

    def fire(self, d):                  #стрельба
        if self.out(d):
            raise BoardOutException()   #исключение точка выстрела за територией поля

        if d in self.busy:
            raise BoardUsedException()  #исключение выстрел в туже точку

        self.busy.append(d)

        for ship in self.squadron:
            if d in ship.ship_coordinates:
                ship.lives -= 1
                self.field[d.x][d.y] = "Х"   #Х в точку попадания корабля
                if ship.lives == 0:
                    self.count += 1
                    self.anticount -= 1 #при потоплении корабля
                    self.environment(ship, verb=True)
                    print("Корабль потоплен!")
                    return False
                else:
                    print("Попадание по борту! ПАНИКА НА КОРАБЛЕ!!!!!")
                    return True

        self.field[d.x][d.y] = "•"
        print("Мимо!")
        return False

    def start(self):
        self.busy = []

class Player:                                   #игроки
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.fire(target)
                return repeat
            except BoardException as e:
                print(e)

class PC(Player):                          #игрок компьютер
    def ask(self):
        t_s = randint(1, 4)    #выбор случайного числа для задержки хода компьютера (типа думает)
        time.sleep(t_s)
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход противника: {d.x + 1} {d.y + 1}')
        return d

class User(Player):                        #игрок человек
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hide = True

        self.ai = PC(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = GameField(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.start()
        return board

    def greet(self):
        print("                         !!!Привет!!!\n"
              "                      Это игра морской бой\n"
              "           Вам предстоит потопить все корабли противника\n"
              "             ход осуществляется вводом координат X и Y\n"
              "          координаты вводятся через пробел сперва X заем Y"
              )

    @staticmethod                  #метод для вывода дсок параллельно
    def vstack(s1, s2):
        s1 = s1.split("\n")
        s2 = s2.split("\n")
        maxlen = max(map(len, s1))
        result = ""
        for line1, line2 in zip(s1, s2):
            result += f"{line1:{maxlen}}    |    {line2}\n"
        return result

    def loop(self):
        num = 0
        while True:
            user_output = (f"Доска пользователя:\nосталось кораблей "
                           f"{self.us.board.anticount}\n\n" + str(self.us.board)   #вывод досок в конслос сподсчётом кораблей
                           )
            ai_output = (f"Доска пользователя:\nосталось кораблей " 
                        f"{self.ai.board.anticount}\n\n" + str(self.ai.board)
                         )
            print("-" * 70)
            print(Game.vstack(user_output, ai_output))
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def go(self):
        self.greet()
        self.loop()

class BoardException(Exception):  #обработка исключений
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass


g = Game()
g.go()