import pygame


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption("Paint")
    clock = pygame.time.Clock()

    radius = 15
    x = 0
    y = 0

    tool = 'pencil'

    color = (0, 0, 255)

    points = []
    shape_start = None

    canvas = pygame.Surface((640, 480))
    canvas.fill((0, 0, 0))

    palette_colors = [
        (255, 0,   0),
        (0,   255, 0),
        (0,   0,   255),
        (255, 255, 0),
        (255, 165, 0),
        (255, 255, 255),
    ]
    palette_rects = []
    for i, c in enumerate(palette_colors):
        palette_rects.append(pygame.Rect(10 + i * 30, 450, 25, 25))

    while True:

        pressed = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        alt_held  = pressed[pygame.K_LALT]  or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_ESCAPE:
                    return

                if event.key == pygame.K_p:
                    tool = 'pencil'
                elif event.key == pygame.K_r:
                    tool = 'rect'
                elif event.key == pygame.K_c:
                    tool = 'circle'
                elif event.key == pygame.K_e:
                    tool = 'eraser'

            if event.type == pygame.MOUSEBUTTONDOWN:
           
                if event.button == 3:
                    radius = max(1, radius - 1)

                if event.button == 1:
                    mx, my = event.pos

                    clicked_palette = False
                    for i, rect in enumerate(palette_rects):
                        if rect.collidepoint(mx, my):
                            color = palette_colors[i]
                            clicked_palette = True
                            break

                    if not clicked_palette:
                        if tool == 'pencil':
                            points = [event.pos]
                        elif tool == 'eraser':
                            points = [event.pos]
                        elif tool in ('rect', 'circle'):
                            shape_start = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                   
                    if tool == 'rect' and shape_start:
                        ex, ey = event.pos
                        sx, sy = shape_start
                        rx = min(sx, ex)
                        ry = min(sy, ey)
                        rw = abs(ex - sx)
                        rh = abs(ey - sy)
                        pygame.draw.rect(canvas, color, (rx, ry, rw, rh), radius)
                        shape_start = None

                    elif tool == 'circle' and shape_start:
                        ex, ey = event.pos
                        sx, sy = shape_start
                        cx = (sx + ex) // 2
                        cy = (sy + ey) // 2
                        rad = int(((ex - sx) ** 2 + (ey - sy) ** 2) ** 0.5 // 2)
                        pygame.draw.circle(canvas, color, (cx, cy), max(1, rad), radius)
                        shape_start = None

                    points = []

            if event.type == pygame.MOUSEMOTION:
                if mouse_buttons[0]:
                    if tool == 'pencil' and points:
                        drawLineBetween(canvas, len(points), points[-1], event.pos, radius, color)
                        points.append(event.pos)
                        points = points[-256:]

                    elif tool == 'eraser':
                        pygame.draw.circle(canvas, (0, 0, 0), event.pos, radius)

        
        screen.blit(canvas, (0, 0))

        for i, rect in enumerate(palette_rects):
            pygame.draw.rect(screen, palette_colors[i], rect)
            if palette_colors[i] == color:
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)

        if shape_start and mouse_buttons[0]:
            mx, my = pygame.mouse.get_pos()
            sx, sy = shape_start
            if tool == 'rect':
                rx = min(sx, mx)
                ry = min(sy, my)
                rw = abs(mx - sx)
                rh = abs(my - sy)
                pygame.draw.rect(screen, color, (rx, ry, rw, rh), radius)
            elif tool == 'circle':
                cx = (sx + mx) // 2
                cy = (sy + my) // 2
                rad = int(((mx - sx) ** 2 + (my - sy) ** 2) ** 0.5 // 2)
                pygame.draw.circle(screen, color, (cx, cy), max(1, rad), radius)

        pygame.display.flip()
        clock.tick(60)


def drawLineBetween(screen, index, start, end, width, color):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))

    for i in range(iterations):
        progress = 1.0 * i / iterations
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(screen, color, (x, y), width)


main()