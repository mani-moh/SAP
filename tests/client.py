import pygame
import socket
import threading
import random

HOST = '127.0.0.1'
PORT = 65432

WIDTH, HEIGHT = 800, 600
BALL_RADIUS = 15

# Ball class
class Ball:
    def __init__(self):
        self.x = random.randint(BALL_RADIUS, WIDTH - BALL_RADIUS)
        self.y = random.randint(BALL_RADIUS, HEIGHT - BALL_RADIUS)
        self.dx = random.choice([-5, 5])
        self.dy = random.choice([-5, 5])
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x < BALL_RADIUS or self.x > WIDTH - BALL_RADIUS:
            self.dx *= -1
        if self.y < BALL_RADIUS or self.y > HEIGHT - BALL_RADIUS:
            self.dy *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), BALL_RADIUS)

# Pygame and network setup
balls = []

def network_listener(sock):
    while True:
        try:
            data = sock.recv(1024)
            if data.decode() == "ADD_BALL":
                balls.append(Ball())
        except:
            break

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        threading.Thread(target=network_listener, args=(s,), daemon=True).start()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((30, 30, 30))
            for ball in balls:
                ball.move()
                ball.draw(screen)

            pygame.display.flip()
            clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
