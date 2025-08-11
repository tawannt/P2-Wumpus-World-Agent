
# 5 predetermined maps of increasing difficulty
PREDETERMINED_MAPS = [
	{
		'desc': 'Easy: No wumpus, no pits, gold at (6,6)',
		'wumpus': [],
		'pits': [],
		'gold': (6, 6)
	},
	{
		'desc': 'Need arrow: 2 wumpus at (2,1) and (1,2), 2 pits (2,3), (5,2), gold at (5,4)',
		'wumpus': [(2, 1), (1, 2)],
		'pits': [],
		'gold': (6, 6)
	},
	{
		'desc': 'Intermediate: 2 wumpus, 3 pits, gold at (5,5)',
		'wumpus': [(1, 5), (6, 5)],
		'pits': [(1, 4), (3, 1), (6, 3)],
		'gold': (5, 5)
	},
	{
		'desc': 'Advanced: 2 wumpus, 6 pits, gold at (2,6)',
		'wumpus': [(4, 3), (4, 4)],
		'pits': [(2, 1), (3, 2), (3, 6), (4, 5), (5, 3), (6, 5)],
		'gold': (2, 6)
	},
	{
		'desc': 'Expert: 2 wumpus, 8 pits, gold at (2,4)',
		'wumpus': [(1, 4), (5, 1)],
		'pits': [(2, 1), (3, 6), (4, 5), (4, 6), (5, 6), (6, 1), (6, 5), (6, 6)],
		'gold': (2, 4)
	}
]

def print_map_preview(map_data):
	size = 6
	board = [["  .  " for _ in range(size)] for _ in range(size)]
	for y, x in map_data['wumpus']:
		board[y-1][x-1] = "  W  "
	for y, x in map_data['pits']:
		board[y-1][x-1] = "  P  "
	gy, gx = map_data['gold']
	board[gy-1][gx-1] = "  G  "
	board[0][0] = "  A  "  # Start
	print(f"\nMap preview: {map_data['desc']}")
	for row in board[::-1]:
		print("|".join(row))

if __name__ == "__main__":
	import sys
	import time
	from environment import WumpusEnvironment
	from knowledgeBase import build_init_kb
	from agent import Explorer
	from astar import WumpusWorldAStar
	from object import Gold, Glitter

	while True:
		print("\nChoose a predetermined map to preview and solve:")
		for i, m in enumerate(PREDETERMINED_MAPS):
			print(f"  {i+1}. {m['desc']}")
		while True:
			try:
				choice = int(input("Enter map number (1-5): "))
				if 1 <= choice <= 5:
					break
			except Exception:
				pass
			print("Invalid input. Please enter a number 1-5.")
		map_data = PREDETERMINED_MAPS[choice-1]
		print_map_preview(map_data)

		# Ask user to run or go back
		while True:
			print("\nOptions:")
			print("  1. Run this map")
			print("  2. Back to map selection")
			opt = input("Enter option (1-2): ").strip()
			if opt == '1':
				# Build environment from map_data
				N = 6
				env = WumpusEnvironment(N=N, K_wumpuses=0, pit_probability=0.0)
				# Clear board and set up manually
				for y in range(1, N+1):
					for x in range(1, N+1):
						env.board[y][x] = []
				# Place wumpus
				for y, x in map_data['wumpus']:
					env.board[y][x].append(__import__('agent').Wumpus())
					env.wumpus_pos.append((y, x))
					# Add stench to adjacent cells
					for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
						ay, ax = y+dy, x+dx
						if 1 <= ay <= N and 1 <= ax <= N:
							if not any(isinstance(e, __import__('object').Stench) for e in env.board[ay][ax]):
								env.board[ay][ax].append(__import__('object').Stench())
				print(f"Placed {len(env.wumpus_pos)} Wumpuses at {env.wumpus_pos}")
				# Place pits
				for y, x in map_data['pits']:
					env.board[y][x].append(__import__('object').Pit())
					# Add breeze to adjacent cells
					for dy, dx in [(-1,0),(1,0),(0,-1),(0,1)]:
						ay, ax = y+dy, x+dx
						if 1 <= ay <= N and 1 <= ax <= N:
							if not any(isinstance(e, __import__('object').Breeze) for e in env.board[ay][ax]):
								env.board[ay][ax].append(__import__('object').Breeze())
				# Place gold
				gy, gx = map_data['gold']
				env.board[gy][gx].append(Gold())
				env.board[gy][gx].append(Glitter())

				# Initialize KB and agent
				kb = build_init_kb(N, env)
				agent = Explorer(kb, pos=(1, 1))
				env.agents = [agent]
				env.board[1][1].append(agent)

				# Create planner
				planner = WumpusWorldAStar(env, kb)

				print("\nInitial board:")
				env.print_board()

				step = 0
				max_steps = 100
				while not env.is_end() and step < max_steps:
					print(f"\n--- STEP {step + 1} ---")
					print(f"Agent at {agent.location}, facing {agent.direction.direction}")
					print(f"Performance: {agent.performance}")
					percepts = env.percept(agent.location)
					planner.update_world_knowledge(agent.location, percepts)
					print(f"Percepts: {[type(p).__name__ for p in percepts]}")
					if any(isinstance(p, Glitter) for p in percepts):
						print("🏆 GOLD DETECTED! Grabbing...")
						env.exe_action(agent, agent.location, 'Grab')
						gold_status = any(isinstance(item, Gold) for item in agent.holding)
						print(f"Gold acquired: {gold_status}")
					action = planner.get_next_action(agent)
					if action:
						print(f"🎯 Planned action: {action}")
						action_percepts = env.exe_action(agent, agent.location, action)
						if not agent.alive:
							print(f"💀 AGENT KILLED BY: {agent.killed_by}")
							break
						if action_percepts:
							for percept in action_percepts:
								print(f"Action result: {type(percept).__name__}")
					else:
						print("❌ No valid action available!")
						break
					print("Board state:")
					env.print_board()
					if agent not in env.agents:
						print("🚀 Agent successfully climbed out!")
						break
					step += 1
					time.sleep(0.3)
				print("\n" + "="*60)
				print("FINAL RESULTS")
				print("="*60)
				print(f"Steps taken: {step}")
				print(f"Final performance: {agent.performance}")
				print(f"Positions visited: {len(planner.visited_positions)}")
				print(f"Visited: {sorted(list(planner.visited_positions))}")
				if not agent.alive:
					print(f"❌ OUTCOME: FAILURE - Agent killed by {agent.killed_by}")
				elif env.gold_taken:
					print("✅ OUTCOME: SUCCESS - Gold found and agent escaped!")
				else:
					print("⚠️  OUTCOME: PARTIAL - Agent escaped but no gold found")
				print(f"Performance score: {agent.performance}")
				sys.exit(0)
			elif opt == '2':
				break
			else:
				print("Invalid option. Please enter 1 or 2.")
	