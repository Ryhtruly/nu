import pygame
import sys
from os import listdir
from os.path import isfile, join


pygame.init()
pygame.display.set_caption("Platformer") 

WIDTH = 1000
HEIGHT = 800
FPS = 60
PLAYER_VEL = 5 

window = pygame.display.set_mode((WIDTH, HEIGHT)) 

start_img = pygame.image.load(join("assets","Other", "start_btn.png"))
exit_img = pygame.image.load(join("assets","Other", "exit_btn.png"))

def draw_intro_screen(window):
    intro_bg_image = pygame.image.load(join("assets","Background", "rsz_new3.png"))
    intro_bg_width, intro_bg_height = intro_bg_image.get_size()

    for x in range(0, WIDTH, intro_bg_width):
        for y in range(0, HEIGHT, intro_bg_height):
            window.blit(intro_bg_image, (x, y))

    font = pygame.font.SysFont(None, 60)
    title_text = font.render('WELCOME TO THE GAME!', True, (255, 255, 255))
    
    start_img_width, start_img_height = start_img.get_size()

    start_button_x = (WIDTH - start_img_width) // 2
    start_button_y = (HEIGHT - start_img_height) // 2
    start_button_rect = pygame.Rect(start_button_x, start_button_y, start_img_width, start_img_height)
    
    window.blit(title_text, ((WIDTH - title_text.get_width()) // 2, HEIGHT // 4))
    
    exit_img_width, exit_img_height = exit_img.get_size()
    exit_button_x = (WIDTH - exit_img_width) // 2
    exit_button_y = start_button_y + start_img_height + 40
    exit_button_rect = pygame.Rect(exit_button_x, exit_button_y, exit_img_width, exit_img_height)

    window.blit(exit_img, exit_button_rect.topleft)

    window.blit(start_img, start_button_rect.topleft)
    
    pygame.display.flip()
    
    return start_button_rect, exit_button_rect


def check_button_event(start_button_rect, exit_button_rect):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_pos):
                return "start"
            if exit_button_rect.collidepoint(mouse_pos):
                pygame.quit()
                sys.exit()
    return None


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, directon = False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width,height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0,0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if directon:
            all_sprites[image.replace(".png","") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites

    print("All Sprites Loaded:", all_sprites)

    return all_sprites

def load_block(size):
    path = join("assets","Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(0 ,0, size, size)
    surface.blit(image, (0,0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = ( 250, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters","VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x , y , width, height):
        super().__init__()

        self.rect = pygame.Rect(x, y , width, height) 
        self.x_vel = 0
        self.y_vel = 0 
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.is_dead = False

    def jump(self):
        self.y_vel = -self.GRAVITY * 9
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        if not self.is_dead: 
            self.hit = True
            self.hit_count += 1
            if self.hit_count >= 2: 
                self.is_dead = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0 

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        if not self.is_dead:
              self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
              self.move(self.x_vel, self.y_vel)
              if self.hit:
                    self.hit_count += 1
              if self.hit_count > fps * 2:
                   self.hit = False
                   self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0 :
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2 :
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction 
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        if self.is_dead:
            font = pygame.font.SysFont('Pixeled', 64)
            text = font.render('DEFEAT', True, (255, 255, 255))
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            win.blit(text, text_rect)

class Object(pygame.sprite.Sprite):
    def __init__(self, x , y , width, height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x, y , width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image,(self.rect.x - offset_x , self.rect.y))

class Block(Object):
    def __init__(self,x, y, size):
        super().__init__(x, y , size, size)
        block = load_block(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x ,y , width, height):
        super().__init__(x, y , width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire",width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "on"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


"""class Fan(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Fan")
        self.fan_sprites = load_sprite_sheets("Traps", "Fan", width, height, True)
        self.image = self.fan_sprites["On"][0]
        self.animation_count = 0
        self.current_state = "On"

    def loop(self):
        sprites = self.fan_sprites[self.current_state]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

    def activate(self):
        self.current_state = "On" """


def get_background(name) :
    image = pygame.image.load(join("assets","Background", name)) 
    _,_, width, height = image.get_rect() 
    tiles = [] 

    for i in range(WIDTH // width +  1): 
        for j in range(HEIGHT // height + 1): 
            pos = [ i * width, j * height]
            tiles.append(pos)  

    return tiles, image

def draw(window , background, bg_image, player, object , offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in object:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
                player.y_vel = 0
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
                player.y_vel = 0

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL )
    collide_right = collide(player, objects, PLAYER_VEL )

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]


    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("rsz_1new2.png")
    start_button_rect, exit_button_rect = draw_intro_screen(window)
    
    while True:
        action = check_button_event(start_button_rect, exit_button_rect)
        if action == "start":
            break
        
    window.fill((255, 255, 255))
    pygame.display.flip()

    block_size = 96

    player = Player(100,100,50,50)

    fires =[
             Fire(block_size * 6.35, HEIGHT - block_size - 64, 16, 32),
             Fire(block_size * 8.35, HEIGHT - block_size - 64, 16, 32),
             Fire(block_size * 10.35, HEIGHT - block_size - 64, 16, 32),
             Fire(block_size * 12.35, HEIGHT - block_size - 64, 16, 32),
             Fire(block_size * 12.35, HEIGHT - block_size - 64, 16, 32),
             Fire(block_size * 14.35, HEIGHT - block_size - 64, 16, 32),
             Fire(block_size * 31.35, HEIGHT - block_size - 64, 16, 32),
    ]

    for fire in fires :
        fire.on()

    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, WIDTH * 10 // block_size)]


    objects = [*floor, *fires]

    pole_start = 2
    pole_end = 7
    for i in range(pole_start, pole_end):
        block_x = 0
        block_y = HEIGHT - block_size * i
        objects.append(Block(block_x, block_y, block_size))

    horizontal1_start = 7
    horizontail1_end = 13

    for i in range(horizontal1_start, horizontail1_end + 2, 2):
        block_x = block_size * i
        block_y = HEIGHT - block_size * 2.5
        objects.append(Block(block_x, block_y, block_size))

    horizontal2_1_start = 16
    horizontail2_1_end  = 27
    for i in range(3, 10):
        for j in range(horizontal2_1_start, horizontail2_1_end + 1):
            block_x = j * block_size
            block_y = HEIGHT - block_size * i
            objects.append(Block(block_x, block_y, block_size))

    objects.append(Block(block_size * 28, HEIGHT - block_size * 3, block_size))

    pole2_start = 2
    pole2_end = 8
    for i in range(pole2_start, pole2_end):
        block_x = block_size * 30
        block_y = HEIGHT - block_size * i
        objects.append(Block(block_x, block_y, block_size))

    objects.append(Block(block_size * 29,HEIGHT - block_size * 4.8, block_size))
    objects.append(Block(block_size * 28, HEIGHT - block_size * 7, block_size))
    objects.append(Block(block_size * 5, HEIGHT - block_size * 2, block_size))

    collums = [7, 6, 5, 4, 3, 2]
    for i in range(32, 37 + 1):
        height = collums[i - 32]
        for j in range(2, height + 1):
            block_x = block_size * i
            block_y = HEIGHT - block_size * j
            objects.append(Block(block_x, block_y, block_size))

    horizontal3_1_start = 39
    horizontal3_1_end = 46
    for i in range(horizontal3_1_start, horizontal3_1_end + 1):
        block_x = block_size * i
        block_y = HEIGHT - block_size * 3
        objects.append(Block(block_x, block_y , block_size))
        block_y2 = HEIGHT - block_size * 5
        objects.append(Block(block_x, block_y2, block_size))

    horizontal3_2_start = 49
    horizontal3_2_end = 56
    for i in range(horizontal3_2_start, horizontal3_2_end + 1):
        block_x = block_size * i
        block_y = HEIGHT - block_size * 4
        objects.append(Block(block_x, block_y, block_size))
        block_y2 = HEIGHT - block_size * 6.5
        objects.append(Block(block_x, block_y2, block_size))

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run :
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2 :
                    player.jump()
        
        player.loop(FPS)
        handle_move(player, objects)

        for fire in fires:
            fire.loop()

        draw(window,background, bg_image, player, objects, offset_x )
        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()

if __name__ == "__main__":
    main(window)