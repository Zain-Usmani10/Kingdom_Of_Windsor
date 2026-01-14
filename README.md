# Medieval Trade Simulator (1450-1470)
A real-time kingdom resource management simulation inspired by Clash Royale, built in Python. Simulate 20 years of medieval trade in 10 minutes.

## Overview
- Manage a kingdom with 11 interconnected cities trading 5 resources (iron, wood, livestock, grain, gold). Each city produces gold plus one resource, with production scaling by population. - - - Cities die if resources fall below survival thresholds.
- Timeline: 1450-1470 (20 years = 10 real minutes, 1 year = 30 seconds)
- Updates: Monthly calculations every 2.5 seconds with animated trade carts

## Random Disasters
1. Drought: No livestock/grain production
2. Pirate Raid: Steals 50% of the stockpile
3. Lightning Storm: Blocks trade route
4. Plague: Isolates city 4 months, kills 10% population/month
5. Labour Strike: No wood/iron production

## Player-Controlled Action
Build in any city during simulation:
1. City Wall (Iron, Wood, Gold): -30% plague impact
2. Refugee Camp (Wood, Livestock, Grain, Gold): +5% production
3. Monument (Gold, Iron): Decorative
4. Granary (Gold, Wood, Grain): 50% grain during drought
5. Hotel (Gold, Iron): +5% gold production

## Interface
- **Map:** Pan/zoom with city dots. Click cities for a detailed view showing resource bars, population charts, construction options, and event logs.
- **Sidebar:** Sustainability score (0-1000) colour-coded red to green.
- **End Report:** Kingdom-wide resource flow, population trends, and decision impacts across multiple tabs.

## Algorithms
**Population:** Linear growth based on resource thresholds<br/>
**Trade:** Balances resources across cities via automated routes<br/>
**Disasters:** Dynamically reroutes resources during events<br/>
**Sustainability:** Scores kingdom on environmental/ethical metrics


Trade: Balances resources across cities via automated routes
Disasters: Dynamically reroutes resources during events
Sustainability: Scores kingdom on environmental/ethical metrics
