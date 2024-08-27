import agentpy as ap
import heapq
from agentToTxt import convert_to_txt

class Obstacle(ap.Agent):
    pass

class AgentNavigator(ap.Agent):
    def setup(self):
        self.trajectory = []
        self.goal_position = None

    def step(self):
        path = self.a_star()
        if path:
            next_position = path[0]
            self.model.grid.move_to(self, next_position)
            self.trajectory.append(next_position)

    def a_star(self):
        start = self.model.grid.positions[self]
        goal = self.goal_position
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, goal)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def heuristic(self, position, goal):
        return abs(position[0] - goal[0]) + abs(position[1] - goal[1])

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.insert(0, current)
        return total_path[1:]

    def get_neighbors(self, position):
        x, y = position
        neighbors = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]

        valid_neighbors = [
            (nx, ny)
            for nx, ny in neighbors
            if 0 <= nx < self.model.p.grid_shape[0] and 0 <= ny < self.model.p.grid_shape[1]
            and not any(isinstance(agent, Obstacle) for agent in self.model.grid.agents[nx, ny])
        ]
        return valid_neighbors

class MultiAgentModel(ap.Model):
    def setup(self):
        self.grid = ap.Grid(self, self.p.grid_shape, track_empty=True)
        self.agents = ap.AgentList(self, 2, AgentNavigator)
        self.grid.add_agents(self.agents, self.p.start_positions)

        for i, agent in enumerate(self.agents):
            agent.goal_position = self.p.goal_positions[i]

        self.obstacles = ap.AgentList(self, len(self.p.obstacle_positions), Obstacle)
        self.grid.add_agents(self.obstacles, self.p.obstacle_positions)

    def step(self):
        self.agents.step()

def run_multi_agent_model(grid_shape, start_positions, goal_positions, obstacle_positions, steps):
    parameters = {
        "steps": steps,
        "grid_shape": grid_shape,
        "start_positions": start_positions,
        "goal_positions": goal_positions,
        "obstacle_positions": obstacle_positions
    }
    model = MultiAgentModel(parameters)
    results = model.run()
    
    agent1_trajectory = model.agents[0].trajectory
    agent2_trajectory = model.agents[1].trajectory
    
    convert_to_txt(agent1_trajectory, agent2_trajectory)
    
    return agent1_trajectory, agent2_trajectory



