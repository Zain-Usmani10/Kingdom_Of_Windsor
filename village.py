import constants as C

class Village:
    def __init__(self, name, produces, position, is_capital=False):
        self.name = name
        self.produces = produces
        self.position = position
        self.is_capital = is_capital
        
        self.population = C.CAPITAL_INITIAL_POPULATION if is_capital else C.INITIAL_POPULATION
        self.growth_rate = 0.0
        
        initial = C.CAPITAL_INITIAL_RESOURCES if is_capital else C.INITIAL_RESOURCES
        self.resources = {res: initial for res in C.RESOURCES}
        
        self.buildings = []
        
        self.active_events = []
        
        self.population_history = []
        self.growth_history = []
        self.event_log = []
        
        self.connected_routes = []
        
        self.is_alive = True
    
    def calculate_thresholds(self):
        survival = C.MINIMUM_SURVIVAL_BASE + (self.population * C.MINIMUM_SURVIVAL_PER_CAPITA)
        growth = C.GROWTH_THRESHOLD_BASE + (self.population * C.GROWTH_THRESHOLD_PER_CAPITA)
        return survival, growth
    
    def calculate_production(self):
        production = {}
        
        has_drought = any(e[0] == 'drought' for e in self.active_events)
        has_strike = any(e[0] == 'strike' for e in self.active_events)
        
        production_bonus = 1.0
        if 'camp' in self.buildings:
            production_bonus = 1.05
        
        gold_bonus = 1.0
        if 'hotel' in self.buildings:
            gold_bonus = 1.05
        
        if self.produces and not self.is_capital:
            base = C.BASE_PRODUCTION
            per_capita = self.population * C.PRODUCTION_PER_CAPITA
            amount = (base + per_capita) * production_bonus
            
            if has_drought and self.produces in ['livestock', 'grain']:
                if self.produces == 'grain' and 'granary' in self.buildings:
                    amount *= 0.5
                else:
                    amount = 0
            
            if has_strike and self.produces in ['wood', 'iron']:
                amount = 0
            
            production[self.produces] = amount
        
        gold_base = C.GOLD_BASE_PRODUCTION
        gold_per_capita = self.population * C.GOLD_PER_CAPITA
        production['gold'] = (gold_base + gold_per_capita) * gold_bonus
        
        return production
    
    def calculate_consumption(self):
        consumption = {}
        for resource in C.RESOURCES:
            consumption[resource] = self.population * C.CONSUMPTION_PER_CAPITA
        return consumption
    
    def calculate_growth_rate(self):
        if not self.is_alive:
            return -1.0
        
        survival_threshold, growth_threshold = self.calculate_thresholds()
        
        for resource in C.RESOURCES:
            if self.resources[resource] < survival_threshold:
                self.is_alive = False
                return -1.0
        
        total_surplus = 0
        total_deficit = 0
        
        for resource in C.RESOURCES:
            if self.resources[resource] >= growth_threshold:
                surplus = self.resources[resource] - growth_threshold
                total_surplus += surplus
            else:
                deficit = growth_threshold - self.resources[resource]
                total_deficit += deficit
        
        if total_deficit == 0:
            growth = min(C.MAX_GROWTH_RATE, total_surplus / (growth_threshold * len(C.RESOURCES)))
        else:
            growth = max(C.MAX_DECLINE_RATE, -total_deficit / (growth_threshold * len(C.RESOURCES)))
        
        return growth
    
    def update_month(self, production, consumption, tax=0):
        for resource, amount in production.items():
            self.resources[resource] += amount
        
        for resource, amount in consumption.items():
            self.resources[resource] -= amount
        
        if not self.is_capital and tax > 0:
            self.resources['gold'] -= tax
        
        self.growth_rate = self.calculate_growth_rate()
        if self.is_alive:
            new_population = self.population * (1 + self.growth_rate)
            self.population = max(100, int(new_population))
        
        self.active_events = [(evt, dur - 1) for evt, dur in self.active_events if dur > 1]
        
        for event_type, _ in self.active_events:
            if event_type == 'plague':
                death_rate = 0.10
                if 'wall' in self.buildings:
                    death_rate *= 0.70
                self.population = int(self.population * (1 - death_rate))
        
        self.population_history.append(self.population)
        self.growth_history.append(self.growth_rate)
    
    def add_event(self, event_type):
        duration = C.EVENT_TYPES[event_type]['duration']
        self.active_events.append((event_type, duration))
        
        event_name = C.EVENT_TYPES[event_type]['name']
        self.event_log.append(event_name)
        
        if event_type == 'pirates':
            for resource in C.RESOURCES:
                self.resources[resource] *= 0.5
    
    def has_event_type(self, event_type):
        return any(e[0] == event_type for e in self.active_events)
    
    def can_afford_building(self, building_type):
        if building_type in self.buildings:
            return False
        
        costs = C.BUILDINGS[building_type]['cost']
        for resource, amount in costs.items():
            if self.resources[resource] < amount:
                return False
        return True
    
    def build_structure(self, building_type):
        if not self.can_afford_building(building_type):
            return False
        
        costs = C.BUILDINGS[building_type]['cost']
        for resource, amount in costs.items():
            self.resources[resource] -= amount
        
        self.buildings.append(building_type)
        self.event_log.append(f"Built {C.BUILDINGS[building_type]['name']}")
        return True