import pygame
import random

pygame.init()

clock = pygame.time.Clock()

speed = 60
screen = pygame.display.set_mode((829, 818))
font = pygame.font.SysFont('Bauhaus 93', 60)  # шрифт для очков
white = (255, 255, 255)  # цвет очков
pygame.display.set_caption('flappy bird')  # название игры
icon = pygame.image.load('images/bird1.png').convert_alpha()  # иконка игры
pygame.display.set_icon(icon)

score = 0

font_score = pygame.font.Font('font/Minecraft Rus NEW.otf', 60)  # тип и размер шрифта

ground = pygame.image.load("images/ground.png").convert_alpha()
font_res = pygame.font.Font(f"font/Minecraft Rus NEW.otf", 35)  # тип и размер шрифта
theme_count = 1
f = open('memory/money.txt', 'r')
money_score = int(f.readline())
f.close()

font_cost = pygame.font.Font(f"font/Minecraft Rus NEW.otf", 10)
f = open('memory/cost.txt', 'r')
cost_list = [i.split() for i in f.readlines()]
f.close()

global max_score
f = open('memory/score.txt', 'r')
max_score = f.readline()
f.close()

f = open('memory/theme.txt', 'r')
theme_count = int(f.readline())
f.close()
background = pygame.image.load(f'images/bg{theme_count}.png').convert()  # загружаем текущую тему


# создаем кнопку выбора птицы
def change_background(operation):  # функция смены фона
    global theme_count
    global background
    theme_count += operation
    if theme_count > 15:
        theme_count = 15
    if theme_count < 1:
        theme_count = 1
    background = pygame.image.load(f'images/bg{theme_count}.png').convert()


def made_icon(width, height, x, y, text='', font=10):  # создаем иконку(для скинов и стоимости)
    but = [0] * 3
    but[0] = pygame.Rect(screen.get_width() / 2 - (100 + width), screen.get_height() / 3 - (20 + height), 200 + x,
                         200 + y)  # X, Y, Ширина, Высота
    but[1] = pygame.Rect(screen.get_width() / 2 - (105 + width), screen.get_height() / 3 - (25 + height), 210 + x,
                         210 + y)  # X, Y, Ширина, Высота
    but[2] = pygame.Rect(screen.get_width() / 2 - (110 + width), screen.get_height() / 3 - (30 + height), 220 + x,
                         220 + y)  # X, Y, Ширина, Высота
    pygame.draw.rect(screen, [65, 25, 0], but[2])  # Рисуем кнопку (коричневый)
    pygame.draw.rect(screen, [255, 255, 255], but[1])  # Рисуем кнопку (белый)
    pygame.draw.rect(screen, [255, 79, 0], but[0])
    font_text = pygame.font.Font(f"font/Minecraft Rus NEW.otf", font)
    icon_text = font_text.render(text, True, (255, 255, 255))
    font_text_rect = icon_text.get_rect(center=but[0].center)  # Выровнять текст по центру кнопки
    screen.blit(icon_text, font_text_rect)
    return but[0]


# создаем кнопки меню
def made_button(x, y, text_but=''):  # создаем текстовую кнопку(отличие от иконки в тени снизу)
    but = [0] * 3
    but[0] = pygame.Rect(screen.get_width() / 2 - (100 + x), screen.get_height() / 3 - (20 + y), 200,
                         80)  # X, Y, Ширина, Высота
    but[1] = pygame.Rect(screen.get_width() / 2 - (105 + x), screen.get_height() / 3 - (25 + y), 210,
                         90)  # X, Y, Ширина, Высота
    but[2] = pygame.Rect(screen.get_width() / 2 - (110 + x), screen.get_height() / 3 - (30 + y), 220,
                         105)  # X, Y, Ширина, Высота
    pygame.draw.rect(screen, [65, 25, 0], but[2])  # Рисуем кнопку (коричневый)
    pygame.draw.rect(screen, [255, 255, 255], but[1])  # Рисуем кнопку (белый)
    pygame.draw.rect(screen, [255, 79, 0], but[0])  # Рисуем кнопку (ораньж)
    restart_text = font_res.render(text_but, True, (255, 255, 255))
    restart_text_rect = restart_text.get_rect(center=but[0].center)  # Выровнять текст по центру кнопки
    screen.blit(restart_text, restart_text_rect)
    return but[2]


# создаем игровые переменные
ground_scroll = 0  # для движения земли
scroll_speed = 4  # скорость движения земли
flying = False  # для начала игры не сразу
game_over = False  # для завершения игры
pipe_gap = 170  # для расстояния между верхней и нижней трубами
pipe_frequency = 1500  # милисекунды
last_pipe = pygame.time.get_ticks() - pipe_frequency  # время генерации последней трубы
bg_sound = pygame.mixer.Sound('sounds/music.mp3')  # музыка игры
bg_sound.set_volume(0.1)
coins_sound = pygame.mixer.Sound('sounds/coins.mp3')  # звук монет
coins_sound.set_volume(1)
game_over_sound = pygame.mixer.Sound('sounds/game over.mp3')  # звук конца игры
game_over_sound.set_volume(0.1)
game_over_sound_played = False


# создаем класс игрока
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, skin):  # создание картинки
        pygame.sprite.Sprite.__init__(self)
        self.skin = skin
        self.images = []  # создаем массив картинок для анимации
        self.counter = 0  # подсчет времени иттерации
        self.bird_anim_count = 0  # контроль номера картинки
        for num in range(1, 4):  # цикл, заполняющий массив картинками
            img = pygame.image.load(f'images/{skin}{num}.png').convert_alpha()
            self.images.append(img)
        self.image = self.images[self.bird_anim_count]  # картинка, котторую будем выводить
        self.rect = self.image.get_rect()  # выводим картинку
        self.rect.center = [x, y]  # местоположение выводимой картинки
        self.vel = 0  # контроль увеличения координаты y
        self.clicked = False  # \для контроля, чтобы птица не поднималась выше при удержании мышки

    def jump(self):
        self.vel = -9  # Устанавливаем скорость прыжка в отрицательное значение для движения вверх
        self.clicked = True

    def update(self):  # обновляем картинку
        if flying == True:  # когда игра начата
            # создание гравитации
            self.vel += 0.5
            if self.vel > 7:  # чтобы более плавно падала
                self.vel = 7
            if self.rect.bottom < 683:
                self.rect.y += int(self.vel)
        if game_over == False:  # если игра не окончена
            # создание прыжка по нажатию мыши или пробела
            if (pygame.mouse.get_pressed()[0] == 1 or pygame.key.get_pressed()[
                pygame.K_SPACE] == 1) and self.clicked == False:  # если нажата правая кнопка мыши или пробел
                self.jump()
            if pygame.mouse.get_pressed()[0] == 0 and pygame.key.get_pressed()[
                pygame.K_SPACE] == 0:  # если правая кнопка мыши разжата
                self.clicked = False
            # анимация полета
            self.counter += 1
            flap_cooldown = 5  # контроль времени переключения картинок
            if self.counter > flap_cooldown:  # делаем смену картинки на следующий номер
                self.counter = 0
                self.bird_anim_count += 1
                if self.bird_anim_count == 3:  # если предыдущая картинка была третьей, то начинаем сначала
                    self.bird_anim_count = 0
            self.image = self.images[self.bird_anim_count]

            # поворот птицы при прыжке и падении
            if self.skin != 'girl':
                self.image = pygame.transform.rotate(self.images[self.bird_anim_count], self.vel * (
                    -2))  # умножили на -, чтобы при падении смотрела вниз, а при прыжке вверх, и на 2, чтобы поворот был больше
        else:  # если игра окончена
            self.image = pygame.transform.rotate(self.images[self.bird_anim_count], -90)


# создаем класс с монетками
class Money(pygame.sprite.Sprite):
    def __init__(self, x, y):  # создание картинки
        pygame.sprite.Sprite.__init__(self)
        self.images = []  # создаем массив картинок для анимации
        self.counter = 0  # подсчет времени иттерации
        self.money_anim_count = 0  # контроль номера картинки
        for num in range(1, 7):  # цикл, заполняющий массив картинками
            img = pygame.image.load(f'images/money{num}.png').convert_alpha()
            self.images.append(img)
        self.image = self.images[self.money_anim_count]  # картинка, котторую будем выводить
        self.rect = self.image.get_rect()  # выводим картинку
        self.rect.center = [x, y]  # местоположение выводимой картинки

    def update(self):
        self.counter += 1
        flap_cooldown = 5  # контроль времени переключения картинок
        if self.counter > flap_cooldown:
            self.counter = 0
            self.money_anim_count += 1
            if self.money_anim_count == 6:  # если предыдущая картинка была шестой, то начинаем сначала
                self.money_anim_count = 0
        self.image = self.images[self.money_anim_count]
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


# создаем класс препятствий
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):  # создание картинки
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('images/pipe.png').convert_alpha()
        self.rect = self.image.get_rect()
        # позиция 1, если труба сверху и 2, если снизу
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)  # если трубф сверху, переворачиваем картинку
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]  # координаты снизу
        if position == 2:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]  # координаты сверху

    def update(self):

        self.rect.x -= scroll_speed
        if self.rect.right < 0:  # обнуляем номер препятствия, когда пролетаем, чтобы потом использовать при счете очков
            self.kill()
            global score
            score += 0.5
            global speed
            if speed < 90:  # Плавно увеличиваем скорость по мере прохождения
                speed += 0.75


bird_group = pygame.sprite.Group()  # создаем группы спрайтов
pipe_group = pygame.sprite.Group()
money_group = pygame.sprite.Group()

flappy = Bird(150, 309, 'bird')  # добавляем птичку
bird_group.add(flappy)
skin_type = 'bird'  # изначально птичка оригинальная
running = True
clicked = False
temp = 0  # количество сложных труб
flag = 0  # флаг на сложные трубы
while running:

    clock.tick(speed)  # фпс
    screen.blit(background, (0, 0))  # вывод заднего фона
    bird_group.draw(screen)  # вывод птички
    bird_group.update()  # обновляем картинку
    money_group.draw(screen)  # выводим монетки
    money_group.update()
    pipe_group.draw(screen)  # вывод трубы

    screen.blit(ground, (ground_scroll, 683))  # вывод земли
    score_text = font_score.render(f' {int(score)}', True, (255, 255, 255))  # вывод текущего счета
    screen.blit(score_text, (screen.get_width() / 2 - 30, 10))

    if int(score) > int(max_score):
        max_score = str(int(score))
    made_icon(270, 230, -80, -150, str("Record: " + max_score), 18)  # создаем рекор в верхнем левом углу
    for event in pygame.event.get():  # закрытие по нажатию кнопки, а не автоматически
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            clicedpos = event.pos

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:  # Проверка нажатия клавиш
            if event.key == pygame.K_SPACE:  # Если нажат пробе
                # Здесь код для прыжка птицы, если игра не окончена
                flappy.jump()

    # если птица ударяется об стенку или потолок, игра окончена
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
        money_group.empty()
        money_group.update()
        speed = 60
        temp = 0
        flag = 0

    # если птица ударяется о землю, игра окончена
    if flappy.rect.bottom >= 683:
        money_group.empty()
        money_group.update()
        game_over = True
        flying = False
        speed = 60
        temp = 0
        flag = 0

    if game_over == False and flying == True:  # если игра не окончена, продолжаем движение

        # создание новых препятствий

        time_now = pygame.time.get_ticks()
        if temp == 0:  # создание обычных препятствий
            if time_now - last_pipe > pipe_frequency:  # если с момента создания прошлой трубы прошло нужное кл-во времени, создаем новую
                pipe_hieght = random.randint(-150, 150)  # рандомное изменение высоты трубы
                top_pipe = Pipe(829, 309 + pipe_hieght, 1)  # ввод верхней трубы
                bottom_pipe = Pipe(829, 309 + pipe_hieght, 2)  # ввод нижней трубы
                flag = 0
                pipe_group.add(bottom_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now

                if int(score) % 5 == 0 and not money_group:  # генерация монеток в каждой 5-й трубе
                    gold = Money(829, pipe_hieght + 300)
                    money_group.add(gold)

        elif temp >= 1:  # сложные трубы

            if score > 0 and int(
                    score) % 15 == 0 and flag == 0:  # определение координат первой сложной трубы(она не выводится )
                pipe_hieght_hard = random.randint(-150, 150)
                flag = 1

            if time_now - last_pipe > 600 and flag == 1:  # генерация сложных труб через короткий интервал и если нашли первую сложную трубу

                pipe_hieght = pipe_hieght_hard + random.randint(-45,
                                                                45)  # меняем координаты в пределах разумного чтобы пользователь мог пролететь
                if 309 + pipe_hieght > 459:
                    pipe_hieght -= 90  # создаем ограничения чтобы трубы не могли выходить дальше опр-го диапазона
                if 309 + pipe_hieght < 159:
                    pipe_hieght += 90

                top_pipe = Pipe(829, 309 + pipe_hieght, 1)  # ввод верхней трубы
                bottom_pipe = Pipe(829, 309 + pipe_hieght, 2)  # ввод нижней трубы
                temp -= 1  # уменьшаем счет труб
                pipe_group.add(bottom_pipe)
                pipe_group.add(top_pipe)
                last_pipe = time_now
                if temp == 3 and not money_group:  # генерацция монетки
                    gold = Money(829, pipe_hieght + 300)
                    money_group.add(gold)
        if int(score) > 0 and int(score) % 15 == 0 and flag == 0:  # провперка счета на вывод сложных труб
            temp = random.randint(4, 7)

        ground_scroll -= scroll_speed  # создание движения земли
        if ground_scroll < -28:  # взяли картинку с запасом, чтобы она оюновлялась незаметно
            ground_scroll = 0
        pipe_group.update()  # обновляем картинку труб

    if pygame.sprite.groupcollide(bird_group, money_group, False, False):  # проверка на то собрала ли птичка монетку
        money_score += 1
        money_group.empty()
        coins_sound.play()

    if game_over == False and flying == False:
        pipe_group.empty()
        bird_group.empty()
        money_group.empty()  # очищаем все
        start_but = made_button(0, 130, 'START')
        skin_but = made_button(0, 0, 'SKIN')
        theme_but = made_button(0, -130,
                                'THEME')  # выводим кнопки старта, скина, меню и стрелочки для выбора темы(конпка темы ни к чему не привязана)
        theme_right = made_icon(-230, -150, -130, -150)
        theme_right_text = font_res.render(">", True, (255, 255, 255))
        theme_text_rect = theme_right_text.get_rect(center=theme_right.center)  # Выровнять текст по центру кнопки
        screen.blit(theme_right_text, theme_text_rect)

        theme_left = made_icon(100, -150, -130, -150)
        theme_left_text = font_res.render("<", True, (255, 255, 255))
        theme_text_rect = theme_left_text.get_rect(center=theme_left.center)  # Выровнять текст по центру кнопки
        screen.blit(theme_left_text, theme_text_rect)

        gold_icon = made_icon(-330, 230, -50, -120)  # выводим кол-во денег в правом верхнем углу
        gold_text = font_res.render(f"$:{money_score}", True, (255, 255, 255))
        gold_text_rect = gold_text.get_rect(center=gold_icon.center)  # Выровнять текст по центру кнопки
        screen.blit(gold_text, gold_text_rect)

        if clicked and theme_right.collidepoint(clicedpos):  # смена фона вправо
            change_background(1)
        if clicked and theme_left.collidepoint(clicedpos):  # смена фона влево
            change_background(-1)

        if clicked and start_but.collidepoint(clicedpos):  # запуск игры на кнопке старт
            score = 1
            # Перезапуск игры (например, создание новой птицы и очистка группы труб)
            bird_group.empty()
            pipe_group.empty()
            flappy = Bird(150, 309, skin_type)
            bird_group.add(flappy)
            flying = True
            clicked = False
            bg_sound.play()
        if clicked and skin_but.collidepoint(clicedpos):  # открытие меню выбора скина
            pipe_group.empty()
            bird_group.empty()
            screen.blit(background, (0, 0))
            screen.blit(ground, (ground_scroll, 683))  # очистка экрана
            skin_icon1 = made_icon(-120, 0, -50, -50)
            skin_icon2 = made_icon(120, 0, -50, -50)
            skin_icon3 = made_icon(120, -200, -50, -50)
            skin_icon4 = made_icon(-120, -200, -50, -50)  # вывод пустых иконок
            skin_type1 = Bird(screen.get_width() / 2 - 145, screen.get_height() / 3 + 55, 'bird')
            skin_type2 = Bird(screen.get_width() / 2 + 100, screen.get_height() / 3 + 55, 'fb')
            skin_type3 = Bird(screen.get_width() / 2 - 145, screen.get_height() / 3 + 255, 'orangebird')
            skin_type4 = Bird(screen.get_width() / 2 + 100, screen.get_height() / 3 + 255,
                              'girl')  # создание вариантов скинов(девочка не дергается при полете)
            bird_group.add(skin_type1)
            bird_group.add(skin_type2)
            bird_group.add(skin_type3)
            bird_group.add(skin_type4)
            bird_group.draw(screen)  # вывод вариантов скина
            gold_icon = made_icon(-330, 230, -50, -120)  # вывод кол-ва денег
            gold_text = font_res.render(f"$:{money_score}", True, (255, 255, 255))
            gold_text_rect = gold_text.get_rect(center=gold_icon.center)  # Выровнять текст по центру кнопки
            screen.blit(gold_text, gold_text_rect)
            pygame.display.update()


            def skin():  # вынесли функцию очистки экрана с последующим выведением скинов для того чтобы выводить стоимость отслеживая курсор мыши(требуется часто обновлять экран)
                screen.blit(background, (0, 0))
                screen.blit(ground, (ground_scroll, 683))
                skin_icon1 = made_icon(-120, 0, -50, -50)
                skin_icon2 = made_icon(120, 0, -50, -50)
                skin_icon3 = made_icon(120, -200, -50, -50)
                skin_icon4 = made_icon(-120, -200, -50, -50)
                bird_group.draw(screen)
                gold_icon = made_icon(-330, 230, -50, -120)
                gold_text = font_res.render(f"$:{money_score}", True, (255, 255, 255))
                gold_text_rect = gold_text.get_rect(center=gold_icon.center)  # Выровнять текст по центру кнопки
                screen.blit(gold_text, gold_text_rect)
                pygame.display.update()


            sk = 1  # флаг для того чтобы отлавливать клик не выходя из цикла
            clicked = False
            while (sk == 1):

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:  # Выход из игры
                        running = False
                        sk = 0

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:  # выход в стартовое меню
                            sk = 0

                    if event.type == pygame.MOUSEBUTTONDOWN:  # отловка клика мыши и его местоположение
                        clicked = True
                        clicedpos = event.pos

                    if not skin_icon1.collidepoint(pygame.mouse.get_pos()) and not skin_icon4.collidepoint(
                            pygame.mouse.get_pos()) and not skin_icon3.collidepoint(pygame.mouse.get_pos()):
                        skin()  # обновление экрана(чтобы очищать экран от иконки со стоимостью)

                    if not clicked and skin_icon1.collidepoint(pygame.mouse.get_pos()) and cost_list[0][
                        2] == 'n':  # если курсор в зоне иконки со скином вывести стоимость рядом с курсором
                        skin()
                        made_icon(300 - pygame.mouse.get_pos()[0], 320 - pygame.mouse.get_pos()[1], -100, -150,
                                  "cost:" + cost_list[0][1], 20)
                        pygame.display.update()
                        clock.tick(30)

                    if not clicked and skin_icon3.collidepoint(pygame.mouse.get_pos()) and cost_list[1][2] == 'n':
                        skin()
                        made_icon(300 - pygame.mouse.get_pos()[0], 320 - pygame.mouse.get_pos()[1], -100, -150,
                                  "cost:" + cost_list[1][1], 20)
                        pygame.display.update()
                        clock.tick(30)

                    if not clicked and skin_icon4.collidepoint(pygame.mouse.get_pos()) and cost_list[2][2] == 'n':
                        skin()
                        made_icon(300 - pygame.mouse.get_pos()[0], 320 - pygame.mouse.get_pos()[1], -100, -150,
                                  "cost:" + cost_list[2][1], 20)
                        pygame.display.update()
                        clock.tick(30)

                    if clicked and skin_icon1.collidepoint(clicedpos):  # проверка на выбор скина
                        if cost_list[0][2] == 'y':  # если скин куплен то установить его
                            skin_type = 'fb'
                            sk = 0
                        elif money_score >= int(cost_list[0][
                                                    1]):  # если скин не куплен то купить его(проверка на то хватит ли денег) и установить как текущий, можно потом оптимизировать
                            cost_list[0][2] = 'y'
                            money_score -= int(cost_list[0][1])
                            skin_type = 'fb'
                            sk = 0

                    if clicked and skin_icon2.collidepoint(clicedpos):
                        skin_type = 'bird'
                        sk = 0

                    if clicked and skin_icon3.collidepoint(clicedpos):
                        if cost_list[1][2] == 'y':
                            skin_type = 'orangebird'
                            sk = 0
                        elif money_score >= int(cost_list[1][1]):
                            cost_list[1][2] = 'y'
                            money_score -= int(cost_list[1][1])
                            skin_type = 'orangebird'
                            sk = 0
                    if clicked and skin_icon4.collidepoint(clicedpos):
                        if cost_list[2][2] == 'y':
                            skin_type = 'girl'
                            sk = 0
                        elif money_score >= int(cost_list[2][1]):
                            cost_list[2][2] = 'y'
                            money_score -= int(cost_list[2][1])
                            skin_type = 'girl'
                            sk = 0
                    clicked = False
            clicked = False
            pygame.display.update()
    # if clicked and theme_but.collidepoint(clicedpos):

    # звук окончания игры
    if game_over and not game_over_sound_played:
        game_over_sound.play()
        game_over_sound_played = True

    # рестарт
    if game_over:  # если птичка врезалась во что то
        flappy = Bird(-150, 309, skin_type)  # заново создаем птичку по координатам начала

        restart_but = made_button(0, 130, 'RESTART')  # создаем кнопки рестарта и меню
        menu_but = made_button(0, 0, 'MENU')
        bg_sound.stop()

        # Проверка нажатия на кнопку
        if clicked and menu_but.collidepoint(clicedpos):  # выход в стартовое меню и обнуление игровых переменных
            game_over = False
            flying = False
            score = 0
            # Перезапуск игры (например, создание новой птицы и очистка группы труб)
            bird_group.empty()
            pipe_group.empty()
            money_group.empty()
            flappy = Bird(150, 309, skin_type)

            clicked = False

        if clicked and restart_but.collidepoint(clicedpos):  # перезапустить саму игру не выходя в главное меню
            # Сброс игровых переменных
            del restart_but
            score = 0
            game_over = False
            # Перезапуск игры (например, создание новой птицы и очистка группы труб)
            bird_group.empty()
            pipe_group.empty()
            money_group.empty()
            flappy = Bird(150, 309, skin_type)
            bird_group.add(flappy)
            flying = True
            clicked = False
            bg_sound.play()
            game_over_sound_played = False
    clicked = False

    pygame.display.update()
f = open('memory/money.txt', 'w')  # сохранение денег в файл
f.write(str(money_score))
f.close()
f = open('memory/cost.txt', 'w')  # сохранение покупок
for i in cost_list:
    f.write(str(i[0] + ' ' + i[1] + ' ' + i[2] + '\n'))

f.close()
f = open('memory/score.txt', 'w')  # сохранение рекорда
f.write(str(max_score))
f.close()

f = open('memory/theme.txt', 'w')  # сохранение текущей темы
f.write(str(theme_count))
pygame.quit()
