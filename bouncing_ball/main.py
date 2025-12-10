import pygame
import numpy as np
from numpy.typing import NDArray
from math import radians, cos, sin, atan2, pi
from random import randint, uniform


pygame.init()
clock = pygame.time.Clock()


class Balls:
    def __init__(self,pos: list[float] | NDArray[np.float64],
                 vel: list[float] | NDArray[np.float64]) -> None:

        self.pos = np.array(pos, dtype=np.float64)
        self.vel = np.array(vel, dtype=np.float64)
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.is_in = True


def create_ball() -> None:
    for _ in range(2):
        ball = Balls(
            pos=[
                randint(int(CIRCLE_CENTER[0] - 75), int(CIRCLE_CENTER[0] + 75)),
                randint(int(CIRCLE_CENTER[1] - 75), int(CIRCLE_CENTER[1] + 75)),
            ],
            vel=[uniform(-4, 4), uniform(-4, 4)],
        )
        balls.append(ball)


def draw_arc(window: pygame.Surface,center: NDArray[np.float64],
             radius: float,start_angle: float,end_angle: float) -> None:

    p1 = center + (radius) * np.array(
        [cos(start_angle), sin(start_angle)], dtype=np.float64
    )
    p2 = center + (radius) * np.array(
        [cos(end_angle), sin(end_angle)], dtype=np.float64
    )
    pygame.draw.polygon(window, BLACK, [center, p1, p2], 0)  # type: ignore[re-def]


def is_ball_can_out(center: NDArray[np.float64], ball_pos: NDArray[np.float64],
                    start_angle: float, end_angle: float) -> bool:

    dx = ball_pos[0] - center[0]
    dy = ball_pos[1] - center[1]

    alpha = atan2(dy, dx)
    start_angle = start_angle % (2 * pi)
    end_angle = end_angle % (2 * pi)

    if start_angle > end_angle:
        end_angle += 2 * pi

    if (start_angle <= alpha <= end_angle) or (
        start_angle <= alpha + 2 * pi <= end_angle):
        return True

    return False


# WINDOW SIZES
WIDTH = 800
HEIGHT = 800

# COLORS
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)

# SHAPES
CIRCLE_CENTER = np.array([WIDTH / 2, HEIGHT / 2], dtype=np.float64)
CIRCLE_RADIUS = 200

# BALLS
ball_pos = np.array([WIDTH / 2, HEIGHT / 2 - 100])
BALL_RADIUS = 5
ball_vel = np.array([0, 0], dtype=np.float64)
balls: list = [Balls(pos=ball_pos, vel=ball_vel)]

# GRAVITY
GRAVITY = 0.2

# ANGLE
ANGLE = 45
start_angle = radians(-ANGLE / 2)
end_angle = radians(ANGLE / 2)
SPINNING_SPEED = 0.01

running = True
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False  # exit the game when ESC is pressed

    start_angle += SPINNING_SPEED
    end_angle += SPINNING_SPEED

    for ball in balls:
        ball.vel[1] += GRAVITY
        ball.pos += ball.vel

        if (
            ball.pos[0] < 0
            or ball.pos[1] < 0
            or ball.pos[0] > WIDTH
            or ball.pos[1] > HEIGHT
        ):
            balls.remove(ball)
            create_ball()

        dist = np.linalg.norm(ball.pos - CIRCLE_CENTER)
        if dist + BALL_RADIUS > CIRCLE_RADIUS:
            if is_ball_can_out(CIRCLE_CENTER, ball.pos, start_angle, end_angle):
                ball.is_in = False

            if ball.is_in:
                direct = ball.pos - CIRCLE_CENTER
                direct_vel_unit = direct / dist

                ball.pos = (
                    direct_vel_unit * (CIRCLE_RADIUS - BALL_RADIUS) + CIRCLE_CENTER
                )

                t = np.array([-direct[1], direct[0]])
                t_unit = np.array(
                    [-direct_vel_unit[1], direct_vel_unit[0]], dtype=np.float64
                )
                t_norm = np.sqrt(sum(t_unit**2))

                proj_bv_on_t = (
                    np.dot(ball.vel, t_unit) / t_norm**2
                ) * t_unit  # bv -> ball.vel

                ball.vel = 2 * proj_bv_on_t - ball.vel
                ball.vel += t * SPINNING_SPEED  # v = r*w

    WINDOW.fill(BLACK)
    pygame.display.set_caption("Bouncing Balls")
    pygame.draw.circle(WINDOW, ORANGE, CIRCLE_CENTER, CIRCLE_RADIUS, 3)  # type: ignore [no-redef]
    draw_arc(WINDOW, CIRCLE_CENTER, CIRCLE_RADIUS + 1000, start_angle, end_angle)
    for ball in balls:
        pygame.draw.circle(WINDOW, ball.color, ball.pos, BALL_RADIUS)  # type: ignore [no-redef]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
