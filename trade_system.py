
import math
import constants as C

class TradeCart:
    def __init__(self, from_village, to_village, resources, start_pos, end_pos):
        self.from_village = from_village
        self.to_village = to_village
        self.resources = resources
        self.position = list(start_pos) 
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.progress = 0.0
        
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        self.distance = math.sqrt(dx*dx + dy*dy)
        self.duration = C.SECONDS_PER_MONTH 
        self.elapsed = 0.0
    
    def update(self, dt):
        self.elapsed += dt
        self.progress = min(1.0, self.elapsed / self.duration)
        
        self.position[0] = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * self.progress
        self.position[1] = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * self.progress
        
        return self.progress >= 1.0  

class TradeSystem:
    def __init__(self, villages):
        self.villages = villages
        self.active_carts = []
    
    def calculate_trades(self):
        trades = [] 
        
        alive_villages = [v for v in self.villages if v.is_alive]
        
        for resource in C.RESOURCES:
            surpluses = [] 
            deficits = []   
            
            for village in alive_villages:
                survival_threshold, growth_threshold = village.calculate_thresholds()
                current = village.resources[resource]
                
                can_receive = not (
                    village.has_event_type('plague') or
                    village.has_event_type('lightning')
                )
                
                if current > growth_threshold:
                    surplus = current - growth_threshold
                    surpluses.append((village, surplus))
                
                elif current < growth_threshold and can_receive:
                    deficit = 2*growth_threshold - current
                    
                    if current < growth_threshold:
                        urgency = 1000/(growth_threshold/(growth_threshold - current))
                    else:
                        urgency = deficit / growth_threshold
                    
                    deficits.append((village, deficit, urgency))
            
            deficits.sort(key=lambda x: x[2], reverse=True)
            
            for deficit_village, deficit_amount, urgency in deficits:
                needed = deficit_amount
                
                surplus_distances = []
                for surplus_village, surplus_amount in surpluses:
                    if surplus_amount > 0:
                        dx = surplus_village.position[0] - deficit_village.position[0]
                        dy = surplus_village.position[1] - deficit_village.position[1]
                        distance = math.sqrt(dx*dx + dy*dy)
                        
                        route_blocked = (
                            surplus_village.has_event_type('lightning') or
                            surplus_village.has_event_type('plague')
                        )
                        
                        if not route_blocked:
                            surplus_distances.append((surplus_village, surplus_amount, distance))
                
                surplus_distances.sort(key=lambda x: x[2])
                
                for surplus_village, surplus_amount, distance in surplus_distances:
                    if needed <= 0:
                        break
                    
                    send_amount = min(needed, surplus_amount) 
                    
                    if send_amount > 5:  
                        trades.append((surplus_village, deficit_village, resource, send_amount))
                        
                        for i, (v, amt) in enumerate(surpluses):
                            if v == surplus_village:
                                surpluses[i] = (v, amt - send_amount)
                                break
                        
                        needed -= send_amount
        
        return trades
    
    def execute_trades(self, trades):
        for from_village, to_village, resource, amount in trades:
            from_village.resources[resource] -= amount
            
            actual_amount = amount * C.TRADE_EFFICIENCY
            
            cart = TradeCart(
                from_village.name,
                to_village.name,
                {resource: actual_amount},
                from_village.position,
                to_village.position
            )
            self.active_carts.append(cart)
    
    def update(self, dt):
        completed = []
        
        for cart in self.active_carts:
            if cart.update(dt):
                completed.append(cart)
        
        for cart in completed:
            for village in self.villages:
                if village.name == cart.to_village:
                    for resource, amount in cart.resources.items():
                        village.resources[resource] += amount
                    break
            
            self.active_carts.remove(cart)