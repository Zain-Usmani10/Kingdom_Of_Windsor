
import constants as C
from village import Village
from trade_system import TradeSystem
from events import EventSystem

class GameEngine:
    def __init__(self):
        self.current_year = C.SIMULATION_START_YEAR
        self.current_month = 1
        self.elapsed_time = 0.0
        self.month_timer = 0.0
        
        self.villages = []
        for city_data in C.CITIES:
            village = Village(
                city_data['name'],
                city_data['produces'],
                city_data['pos'],
                city_data.get('is_capital', False)
            )
            self.villages.append(village)
        
        self._setup_trade_routes()
        
        self.trade_system = TradeSystem(self.villages)
        self.event_system = EventSystem(self.villages)
        
        self.sustainability_score = 500  
        self.sustainability_history = []
        
        self.is_running = True
        self.is_paused = False
        self.simulation_complete = False
        
        self.total_trades = 0
        self.total_deaths = 0
        self.total_events = 0
    
    def _setup_trade_routes(self):
        """Setup trade route connections between villages"""
        import math
        
        for i, village in enumerate(self.villages):
            distances = []
            for j, other in enumerate(self.villages):
                if i != j:
                    dx = village.position[0] - other.position[0]
                    dy = village.position[1] - other.position[1]
                    dist = math.sqrt(dx*dx + dy*dy)
                    distances.append((other.name, dist))
            
            distances.sort(key=lambda x: x[1])
            num_connections = 4 if village.is_capital else 3
            village.connected_routes = [name for name, _ in distances[:num_connections]]
    
    def update(self, dt):
        """Main update loop"""
        if self.simulation_complete:
            return
        
        if not self.is_paused:
            self.elapsed_time += dt
            self.month_timer += dt
            
            if self.month_timer >= C.SECONDS_PER_MONTH:
                self.month_timer -= C.SECONDS_PER_MONTH
                self.update_month()
            
            if self.current_year >= C.SIMULATION_END_YEAR:
                self.simulation_complete = True
        
        self.trade_system.update(dt)
    
    def update_month(self):
        """Process one month cycle"""
        self.current_month += 1
        if self.current_month > C.MONTHS_PER_YEAR:
            self.current_month = 1
            self.current_year += 1
        
        self.event_system.check_and_spawn_events(self.current_year, self.current_month)
        
        capital = None
        total_tax = 0
        
        for village in self.villages:
            if not village.is_alive:
                continue
            
            production = village.calculate_production()
            consumption = village.calculate_consumption()
            
            tax = 0
            if not village.is_capital:
                tax = production.get('gold', 0) * C.CAPITAL_TAX_RATE
                total_tax += tax
            else:
                capital = village
            
            village.update_month(production, consumption, tax)
        
        if capital and capital.is_alive:
            capital.resources['gold'] += total_tax
        
        trades = self.trade_system.calculate_trades()
        self.trade_system.execute_trades(trades)
        self.total_trades += len(trades)
        
        self._update_sustainability_score()
        
        for village in self.villages:
            if not village.is_alive:
                self.total_deaths += 1
    
    def _update_sustainability_score(self):
        score = 0
        weights = C.SUSTAINABILITY_WEIGHTS
        
        resource_variance = []
        for resource in C.RESOURCES:
            total = sum(v.resources[resource] for v in self.villages if v.is_alive)
            resource_variance.append(total)
        
        if resource_variance:
            avg = sum(resource_variance) / len(resource_variance)
            if avg > 0:
                variance_ratio = max(resource_variance) / (min(resource_variance) + 1)
                balance_score = max(0, 1.0 - (variance_ratio - 1) / 10)
                score += balance_score * weights['resource_balance']
        
        alive_villages = [v for v in self.villages if v.is_alive]
        if alive_villages:
            avg_growth = sum(v.growth_rate for v in alive_villages) / len(alive_villages)
            stability_score = max(0, min(1.0, 0.5 + avg_growth * 5))
            
            death_penalty = self.total_deaths / len(self.villages)
            stability_score *= (1 - death_penalty)
            
            score += stability_score * weights['population_stability']
        
        if self.current_month > 1:
            trade_rate = self.total_trades / ((self.current_year - C.SIMULATION_START_YEAR) * 12 + self.current_month)
            efficiency_score = min(1.0, trade_rate / 20)
            score += efficiency_score * weights['trade_efficiency']
        
        total_events = len(self.event_system.event_history)
        if total_events > 0:
            recovery_rate = len(alive_villages) / len(self.villages)
            score += recovery_rate * weights['disaster_recovery']
        else:
            score += 0.5 * weights['disaster_recovery']
        
        total_buildings = sum(len(v.buildings) for v in alive_villages)
        building_types = set()
        for v in alive_villages:
            building_types.update(v.buildings)
        
        if total_buildings > 0:
            diversity_score = len(building_types) / len(C.BUILDINGS)
            score += diversity_score * weights['building_diversity']
        
        self.sustainability_score = int(score)
        self.sustainability_history.append(self.sustainability_score)
    
    def get_capital(self):
        for village in self.villages:
            if village.is_capital:
                return village
        return None
    
    def get_time_string(self):
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return f"{month_names[self.current_month - 1]} {self.current_year}"
    
    def get_progress_percent(self):
        total_months = (C.SIMULATION_END_YEAR - C.SIMULATION_START_YEAR) * 12
        current_months = (self.current_year - C.SIMULATION_START_YEAR) * 12 + self.current_month
        return (current_months / total_months) * 100
    
    def toggle_pause(self):
        self.is_paused = not self.is_paused