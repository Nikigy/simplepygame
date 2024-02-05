import pygame
import random

# Initialize Pygame
pygame.init()

# Set up the game window
window_width = 1000
window_height = 800
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Physics Game")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Define classes

def main_menu(window):
    font = pygame.font.Font(None, 36)
    controls_text = [
        "Controls:",
        "Move: Arrow keys",
        "Strafe: Hold Shift + Arrow keys",
        "Shoot: Space",
        "Press any key to start..."
    ]
    window.fill((0, 0, 0))
    for i, text in enumerate(controls_text):
        surface = font.render(text, True, (255, 255, 255))
        rect = surface.get_rect(center=(window_width // 2, window_height // 2 + i * 40))
        window.blit(surface, rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP:
                return

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (window_width // 2, window_height // 2)
        self.speed = 5
        self.direction = 'up'
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 250  # Shoot delay in milliseconds
        self.health = 50
        self.velocity = pygame.Vector2(0, 0)
        self.friction = -0.1
        self.dot_size = 10
        self.dot_color = (0, 255, 0)  # Color of the dot (green)


    def update(self):
        keys = pygame.key.get_pressed()
        acceleration = pygame.Vector2(0, 0)
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:  # If either shift key is pressed
            if keys[pygame.K_LEFT]:
                acceleration.x = -1
            if keys[pygame.K_RIGHT]:
                acceleration.x = 1
            if keys[pygame.K_UP]:
                acceleration.y = -1
            if keys[pygame.K_DOWN]:
                acceleration.y = 1
        else:  # If no shift key is pressed
            if keys[pygame.K_LEFT]:
                self.direction = "left"
                acceleration.x = -1
            if keys[pygame.K_RIGHT]:
                self.direction = "right"
                acceleration.x = 1
            if keys[pygame.K_UP]:
                self.direction = "up"
                acceleration.y = -1
            if keys[pygame.K_DOWN]:
                self.direction = "down"
                acceleration.y = 1
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction)
                all_sprites.add(bullet)
                bullets.add(bullet)

        # Apply friction
        acceleration += self.velocity * self.friction

        # Update velocity
        self.velocity += acceleration
        # Update position
        self.rect.center += self.velocity

        # Prevent player from leaving the screen
        self.rect.x = max(0, min(self.rect.x, window_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, window_height - self.rect.height))

        # Draw a direction dot on the player
        self.image.fill(RED)
        
        if self.direction == 'up':
            pygame.draw.circle(self.image, self.dot_color, (self.rect.width // 2, 0), self.dot_size)
        elif self.direction == 'down':
            pygame.draw.circle(self.image, self.dot_color, (self.rect.width // 2, self.rect.height), self.dot_size)
        elif self.direction == 'left':
            pygame.draw.circle(self.image, self.dot_color, (0, self.rect.height // 2), self.dot_size)
        elif self.direction == 'right':
            pygame.draw.circle(self.image, self.dot_color, (self.rect.width, self.rect.height // 2), self.dot_size)

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, window_width - self.rect.width)
        self.rect.y = random.randint(0, window_height - self.rect.height)
        self.speed = 1
        self.flanking_speed = 20 
        self.state = "attacking" if random.random() < 0.5 else "flanking"  # Initial state is random
        self.state_switch_time = random.randint(300, 700)  # Random time to switch state
        self.velocity = pygame.Vector2(0, 0)
        self.friction = -0.3

    def avoid_bullets(self, bullets):
        for bullet in bullets:
            dx = bullet.rect.centerx - self.rect.centerx
            dy = bullet.rect.centery - self.rect.centery
            if abs(dx) < 75 and abs(dy) < 75:
                self.velocity.x -= dx / max(abs(dx), 1) * self.speed
                self.velocity.y -= dy / max(abs(dy), 1) * self.speed
                return True 
        return False

    def attack_player(self, player):
        # Attack player from different sides (randomly)
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        if abs(dx) > abs(dy):
            self.velocity.x += dx / max(abs(dx), 1) * self.speed
        else:
            self.velocity.y += dy / max(abs(dy), 1) * self.speed

    def flank_player(self, player, bullets):
        if self.avoid_bullets(bullets):  # If a bullet is close, switch back to "attacking" state
            self.state = "attacking"
        else:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            direction = pygame.math.Vector2(-dy, dx).normalize()  # Perpendicular direction
            flanking_factor = 0.1
            direction *= flanking_factor
            self.velocity.x += (direction.x * self.flanking_speed)
            self.velocity.y += (direction.y * self.flanking_speed)

    def update(self, bullets, player):
        if self.state == "attacking":
            self.avoid_bullets(bullets)
            self.attack_player(player)
            if pygame.time.get_ticks() % self.state_switch_time == 0:  # Switch to "flanking" state after a random time
                self.state = "flanking"
        elif self.state == "flanking":
            self.flank_player(player, bullets)
            if pygame.time.get_ticks() % self.state_switch_time == 0:  # Switch to "attacking" state after a random time
                self.state = "attacking"

        # Apply friction
        acceleration = self.velocity * self.friction
        # Update velocity
        self.velocity += acceleration
        # Update position
        self.rect.center += self.velocity
        # Keep enemy within window bounds
        self.rect.x = max(0, min(self.rect.x, window_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, window_height - self.rect.height))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)  # Use SRCALPHA to allow transparent color
        pygame.draw.circle(self.image, RED, (5, 5), 5)  # Draw a circle
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.direction = direction

    def update(self):
        if self.direction == 'up':
            self.rect.y -= self.speed
        elif self.direction == 'down':
            self.rect.y += self.speed
        elif self.direction == 'left':
            self.rect.x -= self.speed
        elif self.direction == 'right':
            self.rect.x += self.speed
        if self.rect.top < 0 or self.rect.bottom > window_height or self.rect.left < 0 or self.rect.right > window_width:
            self.kill()

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.image = pygame.Surface((self.player.health, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (10, 10)

    def update(self):
        self.image = pygame.Surface((self.player.health, 20))
        self.image.fill(RED)

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Create player object
player = Player()
all_sprites.add(player)

# Create health bar object
health_bar = HealthBar(player)
all_sprites.add(health_bar)

# Create enemy objects
for _ in range(10):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Main menu
main_menu(window)

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    for sprite in all_sprites:
        if isinstance(sprite, Enemy):
            sprite.update(list(bullets), player)
        else:
            sprite.update()

    # Collision detection
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        player.health -= 10  # Decrease health when hit
        if player.health <= 0:
            print("You lose!")
            running = False

    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)

    if len(enemies) == 0:
        # Player wins
        print("You win!")
        running = False

    # Draw
    window.fill((0, 0, 0))
    all_sprites.draw(window)

    # Refresh the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()