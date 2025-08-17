# Wumpus World Agent

This project implements a Wumpus World simulation with both a random agent and an A* (logic-based) agent. The environment supports both classic and advanced (moving wumpus) settings.

## Features
- Interactive setup: choose map size, number of wumpuses, pit probability, and agent type.
- Two agent types:
  - **Random Agent**: Moves randomly, serves as a baseline.
  - **A* Agent**: Uses logical inference and A* search to solve the world.
- Advanced mode: Wumpuses move every 5 actions.
- Step-by-step board visualization in the terminal.

## How to Run
1. **Install Python 3.8+**
2. Clone this repository:
   ```
   git clone <repo-url>
   cd P2-Wumpus-World-Agent
   ```
3. Run the main program:
   ```
   python main.py
   ```
4. Follow the prompts to configure the world and select the agent.

## File Structure
- `main.py` - Entry point, interactive setup and run.
- `environment.py` - Wumpus World environment logic.
- `agent.py` - Agent base classes.
- `astar.py` - Classic A* agent logic.
- `astar_advanced.py` - Advanced A* agent for moving wumpus.
- `random_agent.py` - Random agent logic.
- `knowledgeBase.py`, `direction.py`, `object.py`, `logic.py` - Supporting modules.

## Usage Example
- Choose advanced mode for moving wumpus.
- Select map size, number of wumpuses, and pit probability.
- Pick either Random or A* agent.
- Watch the agent solve the world step by step in the terminal.

## Notes
- The board is printed after every agent action.
- In advanced mode, wumpuses move every 5 actions and the agent replans accordingly.
- The project is modular and easy to extend for new agent types or environment rules.

