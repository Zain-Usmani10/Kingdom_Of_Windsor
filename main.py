import pygame
import sys
from game_engine import GameEngine
from ui_renderer import UIRenderer

pygame.init()

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900
FPS = 60

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Windsor Kingdom Resource Management System")
    clock = pygame.time.Clock()
    
    engine = GameEngine()
    renderer = UIRenderer(screen, engine)
    
    running = True
    frame_count = 0
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            renderer.handle_event(event)
        
        engine.update(dt)
        
        if frame_count % 60 == 0:
            print(f"Year: {engine.current_year}, Month: {engine.current_month}, Carts: {len(engine.trade_system.active_carts)}, Alive: {sum(1 for v in engine.villages if v.is_alive)}")
        
        renderer.render()
        
        pygame.display.flip()
        
        frame_count += 1
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()