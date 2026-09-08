import pygame
import numpy as np
from settings import (
    FOV_ANGLE, NUM_SECTORS, SENSOR_RANGE,
    RED, GREEN, BLACK, YELLOW, BLUE,
)


def draw_food(screen, food):
    pygame.draw.circle(screen, BLUE, (int(food.x), int(food.y)), food.radius)


def _draw_fov(screen, creature):
    half_fov = FOV_ANGLE / 2
    left_angle = creature.angle - half_fov
    right_angle = creature.angle + half_fov

    surface_size = int(SENSOR_RANGE * 2.2)
    surface_half = surface_size // 2

    cos_left = np.cos(left_angle)
    sin_left = np.sin(left_angle)
    cos_right = np.cos(right_angle)
    sin_right = np.sin(right_angle)

    num_arc_points = 12
    fov_points = [(surface_half, surface_half)]
    angle_step = (right_angle - left_angle) / num_arc_points

    for i in range(num_arc_points + 1):
        angle = left_angle + angle_step * i
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        arc_x = surface_half + cos_a * SENSOR_RANGE
        arc_y = surface_half + sin_a * SENSOR_RANGE
        fov_points.append((int(arc_x), int(arc_y)))

    fov_surface = pygame.Surface((surface_size, surface_size), pygame.SRCALPHA)
    pygame.draw.polygon(fov_surface, (255, 255, 0, 10), fov_points)

    blit_x = int(creature.x - surface_half)
    blit_y = int(creature.y - surface_half)
    screen.blit(fov_surface, (blit_x, blit_y))

    sector_angle = FOV_ANGLE / NUM_SECTORS
    cx, cy = int(creature.x), int(creature.y)

    for i in range(NUM_SECTORS + 1):
        sector_line_angle = creature.angle - half_fov + (sector_angle * i)
        cos_sector = np.cos(sector_line_angle)
        sin_sector = np.sin(sector_line_angle)
        line_end_x = cx + cos_sector * SENSOR_RANGE
        line_end_y = cy + sin_sector * SENSOR_RANGE
        pygame.draw.line(
            screen, (200, 200, 0),
            (cx, cy), (int(line_end_x), int(line_end_y)), 1,
        )

    left_end_x = cx + cos_left * SENSOR_RANGE
    left_end_y = cy + sin_left * SENSOR_RANGE
    right_end_x = cx + cos_right * SENSOR_RANGE
    right_end_y = cy + sin_right * SENSOR_RANGE
    pygame.draw.line(screen, YELLOW, (cx, cy), (int(left_end_x), int(left_end_y)))
    pygame.draw.line(screen, YELLOW, (cx, cy), (int(right_end_x), int(right_end_y)))


def _draw_body(screen, creature):
    energy_ratio = min(1, creature.energy / 100)
    green = int(100 + 155 * energy_ratio)
    color = (50, green, 50)
    pygame.draw.circle(screen, color, (int(creature.x), int(creature.y)), creature.radius)

    end_x = creature.x + np.cos(creature.angle) * creature.radius * 1.5
    end_y = creature.y + np.sin(creature.angle) * creature.radius * 1.5
    pygame.draw.line(screen, BLACK, (creature.x, creature.y), (end_x, end_y), 2)


def _draw_energy_bar(screen, creature):
    bar_width = 20
    bar_height = 4
    energy_width = (creature.energy / 150) * bar_width
    pygame.draw.rect(
        screen, RED,
        (creature.x - bar_width // 2, creature.y - creature.radius - 8, bar_width, bar_height),
    )
    pygame.draw.rect(
        screen, GREEN,
        (creature.x - bar_width // 2, creature.y - creature.radius - 8, energy_width, bar_height),
    )


def draw_creature(screen, creature, show_fov=False):
    if not creature.alive:
        pygame.draw.circle(screen, RED, (int(creature.x), int(creature.y)), creature.radius)
        return

    if show_fov:
        _draw_fov(screen, creature)

    _draw_body(screen, creature)
    _draw_energy_bar(screen, creature)
