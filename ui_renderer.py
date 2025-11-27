import pygame
import math
import constants as C

class UIRenderer:
    def __init__(self, screen, engine):
        self.screen = screen
        self.engine = engine
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.view_mode = 'map'
        self.selected_village = None
        
        self.camera_x = 200
        self.camera_y = 0
        self.zoom = 1.6
        self.min_zoom = 0.8
        self.max_zoom = 3.0
        
        self.mouse_down = False
        self.drag_start = None
        
        self._load_assets()
        
        self.building_menu_open = False
        self.hovered_building = None
    
    def _load_assets(self):
        self.assets = {}
        asset_path = 'assets/'
        
        for resource in C.RESOURCES:
            try:
                img = pygame.image.load(f'{asset_path}{resource}_icon.png')
                self.assets[f'{resource}_icon'] = pygame.transform.scale(img, (32, 32))
            except:
                surf = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.circle(surf, C.RESOURCE_COLORS[resource], (16, 16), 14)
                self.assets[f'{resource}_icon'] = surf
        
        for city_data in C.CITIES:
            city_key = city_data['name']
            try:
                if not asset_path.endswith('/'):
                    asset_path += '/'

                img = pygame.image.load(f'{asset_path}{city_key}.png')
                self.assets[f'city_{city_key}'] = img
            except:
                pass
        
        try:
            self.map_bg = pygame.image.load(f'{asset_path}windsor_essex_map.png')
        except:
            self.map_bg = None
    
    def handle_event(self, event):
        if self.view_mode == 'map':
            self._handle_map_event(event)
        elif self.view_mode == 'city_detail':
            self._handle_city_detail_event(event)
        elif self.view_mode == 'end_summary':
            self._handle_end_summary_event(event)
    
    def _handle_map_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_city = self._get_city_at_pos(event.pos)
                if clicked_city:
                    self.view_mode = 'city_detail'
                    self.selected_village = clicked_city
                else:
                    self.mouse_down = True
                    self.drag_start = event.pos
            
            elif event.button == 4:
                old_zoom = self.zoom
                self.zoom = min(self.max_zoom, self.zoom * 1.1)
                
                mouse_world_x = (event.pos[0] - self.camera_x) / old_zoom
                mouse_world_y = (event.pos[1] - self.camera_y) / old_zoom
                
                self.camera_x = event.pos[0] - mouse_world_x * self.zoom
                self.camera_y = event.pos[1] - mouse_world_y * self.zoom
                
            elif event.button == 5:
                old_zoom = self.zoom
                self.zoom = max(self.min_zoom, self.zoom / 1.1)
                
                mouse_world_x = (event.pos[0] - self.camera_x) / old_zoom
                mouse_world_y = (event.pos[1] - self.camera_y) / old_zoom
                
                self.camera_x = event.pos[0] - mouse_world_x * self.zoom
                self.camera_y = event.pos[1] - mouse_world_y * self.zoom
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_down = False
                self.drag_start = None
        
        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_down and self.drag_start:
                dx = event.pos[0] - self.drag_start[0]
                dy = event.pos[1] - self.drag_start[1]
                self.camera_x += dx
                self.camera_y += dy
                self.drag_start = event.pos
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.engine.toggle_pause()
            elif event.key == pygame.K_ESCAPE:
                if self.engine.simulation_complete:
                    self.view_mode = 'end_summary'
    
    def _handle_city_detail_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.selected_village:
                building_y_start = 175
                for i, (building_type, building_data) in enumerate(C.BUILDINGS.items()):
                    button_rect = pygame.Rect(1150, building_y_start + i * 90, 380, 70)
                    if button_rect.collidepoint(event.pos):
                        if self.selected_village.can_afford_building(building_type):
                            success = self.selected_village.build_structure(building_type)
                            if success:
                                print(f"Built {building_data['name']} in {self.selected_village.name}")
                        else:
                            print(f"Cannot afford {building_data['name']}")
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                self.view_mode = 'map'
    
    def _handle_end_summary_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.view_mode = 'map'
    
    def _get_city_at_pos(self, pos):
        for village in self.engine.villages:
            screen_x = village.position[0] * self.zoom + self.camera_x
            screen_y = village.position[1] * self.zoom + self.camera_y
            
            dist = math.sqrt((pos[0] - screen_x)**2 + (pos[1] - screen_y)**2)
            
            radius = 20 * self.zoom
            if dist < radius:
                return village
        
        return None
    
    def world_to_screen(self, world_x, world_y):
        screen_x = world_x * self.zoom + self.camera_x
        screen_y = world_y * self.zoom + self.camera_y
        return (screen_x, screen_y)
    
    def render(self):
        if self.view_mode == 'map':
            self._render_map_view()
        elif self.view_mode == 'city_detail':
            self._render_city_detail()
        elif self.view_mode == 'end_summary':
            self._render_end_summary()
        
        if self.engine.simulation_complete and self.view_mode == 'map':
            self._render_completion_message()
    
    def _render_map_view(self):
        self.screen.fill(C.COLOR_BG)
        
        if self.map_bg:
            bg_width = int(self.map_bg.get_width() * self.zoom)
            bg_height = int(self.map_bg.get_height() * self.zoom)
            scaled_bg = pygame.transform.scale(self.map_bg, (bg_width, bg_height))
            self.screen.blit(scaled_bg, (self.camera_x, self.camera_y))
        
        self._render_trade_routes()
        self._render_trade_carts()
        self._render_cities()
        self._render_ui_overlay()
    
    def _render_trade_routes(self):
        for village in self.engine.villages:
            if not village.is_alive:
                continue
            
            for connected_name in village.connected_routes:
                for other in self.engine.villages:
                    if other.name == connected_name and other.is_alive:
                        color = C.COLOR_ROUTE
                        if village.has_event_type('lightning') or other.has_event_type('lightning'):
                            color = (200, 200, 200)
                        
                        start_pos = self.world_to_screen(village.position[0], village.position[1])
                        end_pos = self.world_to_screen(other.position[0], other.position[1])
                        
                        pygame.draw.line(self.screen, color, start_pos, end_pos, max(1, int(2 * self.zoom)))
                        break
    
    def _render_trade_carts(self):
        for cart in self.engine.trade_system.active_carts:
            screen_pos = self.world_to_screen(cart.position[0], cart.position[1])
            
            radius = max(4, int(6 * self.zoom))
            pygame.draw.circle(self.screen, C.COLOR_CART, screen_pos, radius)
            
            if cart.resources and self.zoom > 1.2:
                resource = list(cart.resources.keys())[0]
                if f'{resource}_icon' in self.assets:
                    icon = self.assets[f'{resource}_icon']
                    icon_size = max(12, int(16 * self.zoom))
                    icon_small = pygame.transform.scale(icon, (icon_size, icon_size))
                    icon_pos = (screen_pos[0] - icon_size//2, screen_pos[1] - icon_size - 10)
                    self.screen.blit(icon_small, icon_pos)

    def _render_cities(self):
        for village in self.engine.villages:
            screen_pos = self.world_to_screen(village.position[0], village.position[1])
            
            if not village.is_alive:
                size = int(15 * self.zoom)
                pygame.draw.line(self.screen, (100, 100, 100), 
                               (screen_pos[0]-size, screen_pos[1]-size),
                               (screen_pos[0]+size, screen_pos[1]+size), max(2, int(3 * self.zoom)))
                pygame.draw.line(self.screen, (100, 100, 100),
                               (screen_pos[0]+size, screen_pos[1]-size),
                               (screen_pos[0]-size, screen_pos[1]+size), max(2, int(3 * self.zoom)))
                
                dead_text = self.font_tiny.render("DEAD", True, (100, 100, 100))
                self.screen.blit(dead_text, (screen_pos[0] - 15, screen_pos[1] - 40))
                continue
            
            city_key = village.name
            city_image = self.assets.get(f'city_{city_key}')
            
            if city_image:
                img_size = int(50 * self.zoom)
                scaled_city = pygame.transform.scale(city_image, (img_size, img_size))
                img_pos = (int(screen_pos[0] - img_size // 2), int(screen_pos[1] - img_size // 2))
                self.screen.blit(scaled_city, img_pos)
                
                border_color = (200, 0, 0) if village.is_capital else (0, 0, 200)
                border_rect = pygame.Rect(img_pos[0], img_pos[1], img_size, img_size)
                pygame.draw.rect(self.screen, border_color, border_rect, max(2, int(3 * self.zoom)))
            else:
                color = C.COLOR_CAPITAL if village.is_capital else C.COLOR_CITY
                radius = int(20 * self.zoom)
                pygame.draw.circle(self.screen, color, screen_pos, radius)
                pygame.draw.circle(self.screen, (0, 0, 0), screen_pos, radius, max(1, int(2 * self.zoom)))
            
            name_text = self.font_small.render(village.name, True, C.COLOR_TEXT)
            name_rect = name_text.get_rect(center=(screen_pos[0], screen_pos[1] - int(35 * self.zoom)))
            self.screen.blit(name_text, name_rect)
            
            if village.produces:
                icon = self.assets.get(f'{village.produces}_icon')
                if icon:
                    icon_size = int(24 * self.zoom)
                    icon_scaled = pygame.transform.scale(icon, (icon_size, icon_size))
                    icon_pos = (int(screen_pos[0] + 30 * self.zoom), int(screen_pos[1] - 12 * self.zoom))
                    self.screen.blit(icon_scaled, icon_pos)
            
            gold_icon = self.assets.get('gold_icon')
            if gold_icon:
                gold_size = int(20 * self.zoom)
                gold_scaled = pygame.transform.scale(gold_icon, (gold_size, gold_size))
                gold_pos = (int(screen_pos[0] + 30 * self.zoom), int(screen_pos[1] + 12 * self.zoom))
                self.screen.blit(gold_scaled, gold_pos)
            
            if self.zoom > 1.8:
                production = village.calculate_production()
                y_offset = 35
                prod_x = int(screen_pos[0] + 50 * self.zoom)
                
                for resource, amount in production.items():
                    amount_text = self.font_tiny.render(f"+{int(amount)}", True, (0, 150, 0))
                    self.screen.blit(amount_text, (prod_x, int(screen_pos[1] + y_offset * self.zoom)))
                    y_offset += 18
                
                pop_text = self.font_tiny.render(f"Pop: {village.population}", True, C.COLOR_TEXT)
                self.screen.blit(pop_text, (int(screen_pos[0] - 30 * self.zoom), int(screen_pos[1] + 40 * self.zoom)))
                
                growth_color = (0, 150, 0) if village.growth_rate > 0 else (150, 0, 0)
                growth_text = self.font_tiny.render(f"{village.growth_rate*100:.1f}%", True, growth_color)
                self.screen.blit(growth_text, (int(screen_pos[0] - 30 * self.zoom), int(screen_pos[1] + 55 * self.zoom)))
            
            if village.active_events:
                event_x = int(screen_pos[0] - 15 * self.zoom)
                for i, (event_type, duration) in enumerate(village.active_events):
                    event_data = C.EVENT_TYPES[event_type]
                    event_text = self.font_medium.render(event_data['icon'], True, event_data['color'])
                    event_pos = (event_x, int(screen_pos[1] - (60 + i * 30) * self.zoom))
                    self.screen.blit(event_text, event_pos)
            
            if village.buildings:
                building_x = int(screen_pos[0] + 30 * self.zoom)
                for i, building_type in enumerate(village.buildings):
                    building_data = C.BUILDINGS[building_type]
                    building_text = self.font_small.render(building_data['icon'], True, building_data['color'])
                    building_pos = (building_x + int(i * 25 * self.zoom), int(screen_pos[1] + 30 * self.zoom))
                    self.screen.blit(building_text, building_pos)
    
    def _render_ui_overlay(self):
        sidebar_rect = pygame.Rect(0, 0, 250, self.height)
        sidebar_surface = pygame.Surface((250, self.height))
        sidebar_surface.set_alpha(220)
        sidebar_surface.fill((50, 40, 30))
        self.screen.blit(sidebar_surface, sidebar_rect)
        
        time_text = self.font_large.render(self.engine.get_time_string(), True, (255, 255, 255))
        self.screen.blit(time_text, (15, 15))
        
        progress = self.engine.get_progress_percent()
        pygame.draw.rect(self.screen, (100, 100, 100), (15, 70, 220, 25))
        pygame.draw.rect(self.screen, (100, 200, 100), (15, 70, int(220 * progress / 100), 25))
        progress_text = self.font_small.render(f"{progress:.1f}%", True, (255, 255, 255))
        self.screen.blit(progress_text, (100, 72))
        
        sus_y = 120
        sus_label = self.font_medium.render("Sustainability", True, (255, 255, 255))
        self.screen.blit(sus_label, (15, sus_y))

        # FIX: Clamp sustainability score to valid range
        sus_score = max(0, min(1000, self.engine.sustainability_score))
        #           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #           CRITICAL: Force score between 0-1000

        sus_height = 250
        sus_filled = int((sus_score / 1000) * sus_height)

        if sus_score < 333:
            red = 255
            green = int(max(0, min(255, (sus_score / 333) * 255)))
            blue = 0
            bar_color = (red, green, blue)
        elif sus_score < 666:
            red = int(max(0, min(255, 255 - ((sus_score - 333) / 333) * 255)))
            green = 255
            blue = 0
            bar_color = (red, green, blue)
        else:
            bar_color = (0, 255, 0)

        pygame.draw.rect(self.screen, (80, 80, 80), (15, sus_y + 35, 50, sus_height))
        pygame.draw.rect(self.screen, bar_color, (15, sus_y + 35 + sus_height - sus_filled, 50, sus_filled))
        
        sus_text = self.font_small.render(f"{sus_score}/1000", True, (255, 255, 255))
        self.screen.blit(sus_text, (75, sus_y + 35 + sus_height // 2))
        
        stats_y = sus_y + sus_height + 60
        stats_label = self.font_medium.render("Kingdom Stats", True, (255, 255, 255))
        self.screen.blit(stats_label, (15, stats_y))
        
        alive_cities = sum(1 for v in self.engine.villages if v.is_alive)
        total_pop = sum(v.population for v in self.engine.villages if v.is_alive)
        
        stats = [
            f"Cities: {alive_cities}/{len(self.engine.villages)}",
            f"Pop: {total_pop:,}",
            f"Carts: {len(self.engine.trade_system.active_carts)}",
            f"Trades: {self.engine.total_trades}",
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font_small.render(stat, True, (255, 255, 255))
            self.screen.blit(stat_text, (15, stats_y + 35 + i * 28))
        
        if self.engine.is_paused:
            pause_text = self.font_large.render("PAUSED", True, (255, 100, 100))
            pause_rect = pause_text.get_rect(center=(self.width // 2, 50))
            self.screen.blit(pause_text, pause_rect)
        
        hint_text = self.font_tiny.render("SPACE: Pause | Drag: Pan | Scroll: Zoom | Click City: Details", True, (200, 200, 200))
        self.screen.blit(hint_text, (self.width - 550, self.height - 25))
    
    def _render_city_detail(self):
        if not self.selected_village:
            self.view_mode = 'map'
            return
        
        village = self.selected_village
        
        self.screen.fill(C.COLOR_BG)
        
        title_text = self.font_large.render(village.name, True, C.COLOR_TEXT)
        self.screen.blit(title_text, (40, 25))
        
        back_text = self.font_small.render("Press ESC to return to map", True, (100, 100, 100))
        self.screen.blit(back_text, (40, 75))
        
        bars_x = 40
        bars_y = 130
        bar_width = 500
        bar_height = 50
        
        survival_threshold, growth_threshold = village.calculate_thresholds()
        
        bar_label = self.font_medium.render("Resource Reserves", True, C.COLOR_TEXT)
        self.screen.blit(bar_label, (bars_x, bars_y - 35))
        
        for i, resource in enumerate(C.RESOURCES):
            y = bars_y + i * (bar_height + 18)
            
            icon = self.assets.get(f'{resource}_icon')
            if icon:
                self.screen.blit(icon, (bars_x, y + 10))
            
            res_name = self.font_small.render(resource.capitalize(), True, C.COLOR_TEXT)
            self.screen.blit(res_name, (bars_x + 38, y + 18))
            
            bar_rect = pygame.Rect(bars_x + 130, y, bar_width, bar_height)
            pygame.draw.rect(self.screen, (200, 200, 200), bar_rect)
            
            max_display = max(300, growth_threshold * 3)
            current = village.resources[resource]
            fill_width = int((min(current, max_display) / max_display) * bar_width)
            fill_rect = pygame.Rect(bars_x + 130, y, fill_width, bar_height)
            pygame.draw.rect(self.screen, C.RESOURCE_COLORS[resource], fill_rect)
            
            survival_x = bars_x + 130 + int((survival_threshold / max_display) * bar_width)
            if survival_x < bars_x + 130 + bar_width:
                pygame.draw.line(self.screen, (255, 0, 0), (survival_x, y), (survival_x, y + bar_height), 3)
            
            growth_x = bars_x + 130 + int((growth_threshold / max_display) * bar_width)
            if growth_x < bars_x + 130 + bar_width:
                pygame.draw.line(self.screen, (255, 255, 0), (growth_x, y), (growth_x, y + bar_height), 3)
            
            amount_text = self.font_small.render(f"{int(current)}", True, C.COLOR_TEXT)
            self.screen.blit(amount_text, (bars_x + 640, y + 18))
            
            pygame.draw.rect(self.screen, C.COLOR_TEXT, bar_rect, 2)
        
        legend_y = bars_y + len(C.RESOURCES) * (bar_height + 18) + 15
        pygame.draw.line(self.screen, (255, 0, 0), (bars_x, legend_y), (bars_x + 25, legend_y), 3)
        legend1 = self.font_tiny.render("Death Threshold", True, C.COLOR_TEXT)
        self.screen.blit(legend1, (bars_x + 32, legend_y - 7))
        
        pygame.draw.line(self.screen, (255, 255, 0), (bars_x + 160, legend_y), (bars_x + 185, legend_y), 3)
        legend2 = self.font_tiny.render("Growth Threshold", True, C.COLOR_TEXT)
        self.screen.blit(legend2, (bars_x + 192, legend_y - 7))
        
        self._render_mini_chart(750, 130, 380, 180, village.population_history, "Population", (100, 100, 200))
        self._render_mini_chart(750, 350, 380, 180, village.growth_history, "Growth Rate", (100, 200, 100))
        
        log_y = 570
        log_label = self.font_medium.render("Event Log", True, C.COLOR_TEXT)
        self.screen.blit(log_label, (40, log_y))
        
        if not village.event_log:
            no_events = self.font_small.render("No events yet", True, (150, 150, 150))
            self.screen.blit(no_events, (40, log_y + 35))
        else:
            recent_events = village.event_log[-8:]
            for i, event in enumerate(recent_events):
                event_text = self.font_small.render(f"• {event}", True, C.COLOR_TEXT)
                self.screen.blit(event_text, (40, log_y + 35 + i * 24))
        
        self._render_building_menu(1150, 130, village)
    
    def _render_mini_chart(self, x, y, width, height, data, title, color):
        chart_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (240, 240, 240), chart_rect)
        pygame.draw.rect(self.screen, C.COLOR_TEXT, chart_rect, 2)
        
        title_text = self.font_medium.render(title, True, C.COLOR_TEXT)
        self.screen.blit(title_text, (x + 10, y + 8))
        
        if not data or len(data) < 2:
            no_data_text = self.font_tiny.render("No data yet", True, (150, 150, 150))
            self.screen.blit(no_data_text, (x + width // 2 - 30, y + height // 2))
            return
        
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        y_axis_x = x + 40
        graph_width = width - 50
        graph_height = height - 50
        
        min_label = self.font_tiny.render(f"{int(min_val)}", True, C.COLOR_TEXT)
        self.screen.blit(min_label, (x + 5, y + height - 25))
        
        max_label = self.font_tiny.render(f"{int(max_val)}", True, C.COLOR_TEXT)
        self.screen.blit(max_label, (x + 5, y + 35))
        
        pygame.draw.line(self.screen, (150, 150, 150), (y_axis_x, y + 35), (y_axis_x, y + height - 15), 1)
        pygame.draw.line(self.screen, (150, 150, 150), (y_axis_x, y + height - 15), (x + width - 10, y + height - 15), 1)
        
        points = []
        for i, val in enumerate(data):
            px = y_axis_x + (i / max(len(data) - 1, 1)) * graph_width
            py = y + height - 15 - ((val - min_val) / range_val) * graph_height
            points.append((px, py))
        
        if len(points) > 1:
            pygame.draw.lines(self.screen, color, False, points, 2)
        
        for point in points:
            pygame.draw.circle(self.screen, color, (int(point[0]), int(point[1])), 3)
    
    def _render_building_menu(self, x, y, village):
        menu_label = self.font_medium.render("Build Projects", True, C.COLOR_TEXT)
        self.screen.blit(menu_label, (x, y))
        
        button_y = y + 45
        for building_type, building_data in C.BUILDINGS.items():
            has_building = building_type in village.buildings
            can_afford = village.can_afford_building(building_type)
            
            button_rect = pygame.Rect(x, button_y, 350, 70)
            if has_building:
                button_color = (100, 150, 100)
            elif can_afford:
                button_color = (150, 150, 200)
            else:
                button_color = (150, 100, 100)
            
            pygame.draw.rect(self.screen, button_color, button_rect)
            pygame.draw.rect(self.screen, C.COLOR_TEXT, button_rect, 2)
            
            icon_text = self.font_medium.render(building_data['icon'], True, building_data['color'])
            self.screen.blit(icon_text, (x + 8, button_y + 8))
            
            name_text = self.font_small.render(building_data['name'], True, C.COLOR_TEXT)
            self.screen.blit(name_text, (x + 42, button_y + 8))
            
            cost_str = ", ".join([f"{amt} {res}" for res, amt in building_data['cost'].items()])
            cost_text = self.font_tiny.render(f"Cost: {cost_str}", True, C.COLOR_TEXT)
            self.screen.blit(cost_text, (x + 42, button_y + 32))
            
            if has_building:
                status_text = self.font_tiny.render("BUILT", True, (0, 100, 0))
            elif can_afford:
                status_text = self.font_tiny.render("Click to build", True, (0, 0, 100))
            else:
                status_text = self.font_tiny.render("Cannot afford", True, (100, 0, 0))
            
            self.screen.blit(status_text, (x + 42, button_y + 50))
            
            button_y += 90
    
    def _render_end_summary(self):
        self.screen.fill(C.COLOR_BG)
        
        title_text = self.font_large.render("Simulation Complete - Kingdom Summary", True, C.COLOR_TEXT)
        title_rect = title_text.get_rect(center=(self.width // 2, 40))
        self.screen.blit(title_text, title_rect)
        
        alive_cities = [v for v in self.engine.villages if v.is_alive]
        total_pop = sum(v.population for v in alive_cities)
        
        stats_y = 120
        stats = [
            f"Simulation Period: {C.SIMULATION_START_YEAR} - {C.SIMULATION_END_YEAR}",
            f"",
            f"Final Cities Alive: {len(alive_cities)} / {len(self.engine.villages)}",
            f"Total Population: {total_pop:,}",
            f"Total Trades Completed: {self.engine.total_trades}",
            f"Total Events: {len(self.engine.event_system.event_history)}",
            f"",
            f"Final Sustainability Score: {self.engine.sustainability_score} / 1000",
        ]
        
        for i, stat in enumerate(stats):
            stat_text = self.font_medium.render(stat, True, C.COLOR_TEXT)
            stat_rect = stat_text.get_rect(center=(self.width // 2, stats_y + i * 38))
            self.screen.blit(stat_text, stat_rect)
        
        breakdown_y = stats_y + len(stats) * 38 + 40
        breakdown_label = self.font_medium.render("City Status:", True, C.COLOR_TEXT)
        self.screen.blit(breakdown_label, (80, breakdown_y))
        
        for i, village in enumerate(self.engine.villages):
            city_y = breakdown_y + 40 + i * 28
            status = "ALIVE" if village.is_alive else "DESTROYED"
            status_color = (0, 150, 0) if village.is_alive else (150, 0, 0)
            
            city_text = self.font_small.render(f"{village.name}: {status}", True, status_color)
            self.screen.blit(city_text, (80, city_y))
            
            if village.is_alive:
                pop_text = self.font_small.render(f"Population: {village.population:,}", True, C.COLOR_TEXT)
                self.screen.blit(pop_text, (350, city_y))
        
        hint_text = self.font_medium.render("Press ESC to return to map", True, (100, 100, 100))
        hint_rect = hint_text.get_rect(center=(self.width // 2, self.height - 40))
        self.screen.blit(hint_text, hint_rect)
    
    def _render_completion_message(self):
        overlay = pygame.Surface((self.width, 180))
        overlay.set_alpha(220)
        overlay.fill((50, 50, 50))
        self.screen.blit(overlay, (0, self.height // 2 - 90))
        
        msg_text = self.font_large.render("Simulation Complete!", True, (255, 255, 100))
        msg_rect = msg_text.get_rect(center=(self.width // 2, self.height // 2 - 25))
        self.screen.blit(msg_text, msg_rect)
        
        hint_text = self.font_medium.render("Press ESC to view final summary", True, (255, 255, 255))
        hint_rect = hint_text.get_rect(center=(self.width // 2, self.height // 2 + 25))
        self.screen.blit(hint_text, hint_rect)