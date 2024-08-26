import agentpy as ap
import heapq
import matplotlib.pyplot as plt

# Guardamos los puntos que reccoren cada agente en una lista de tuples (x,y)
agent1_trajectory = []
agent2_trajectory = []

# Un obstaculo es herencia de Agente
class Obstacle(ap.Agent):
    pass


class AgentNavigator(ap.Agent):

    def setup(self):
        self.trajectory = []
        self.goal_position = None  # la posición meta del agente

    def step(self):
        # En el primer step definimos la meta
        if self.goal_position is None:
            x, y = self.model.grid.positions[self]
            if (x, y) == (9, 0):
                self.goal_position = (x, 9)  # la meta es cualquier x, y = 9
            elif (x, y) == (0, 9):
                self.goal_position = (x, 0)  #la meta es cualquier x, y = 0

        # Encontramos el camino usando el algoritmo A*
        path = self.a_star()
        if path:
            next_position = path[0]  # Get the next position in the path
            self.model.grid.move_to(self, next_position)  # Move the agent
            self.trajectory.append(next_position)  # Record the trajectory

            # Append the coordinates to the global trajectory arrays
            if self.model.agents.index(self) == 0:
                agent1_trajectory.append(next_position)
            else:
                agent2_trajectory.append(next_position)

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
                tentative_g_score = g_score[current] + 1  # Distance from start to neighbor

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []  # No path found

    def heuristic(self, position, goal):
        # Usamos la distancia manhattan como nuestro heurístico
        return abs(position[0] - goal[0]) + abs(position[1] - goal[1])

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.insert(0, current)
        return total_path[1:]  # Return path without the starting point

    def get_neighbors(self, position):
        x, y = position
        neighbors = [(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]

        # Filter out neighbors that are out of bounds or contain obstacles
        valid_neighbors = [
            (nx, ny)
            for nx, ny in neighbors
            if 0 <= nx < self.model.grid.shape[0] and 0 <= ny < self.model.grid.shape[1]
            and (nx, ny) not in self.model.grid.positions.values()
        ]
        return valid_neighbors


class MultiAgentModel(ap.Model):

    def setup(self):
        # Initialize grid, agents, and obstacles
        self.grid = ap.Grid(self, (10, 10), track_empty=True)
        self.agents = ap.AgentList(self, 2, AgentNavigator)
        self.grid.add_agents(self.agents, [(9, 0), (0, 9)])  # Initial positions at (9, 0) and (0, 9)

        # Define obstacles (you can specify the locations here)
        obstacle_positions = [(0,5),(1,5),(2,5),(3, 5), (5, 5), (6, 5),(7,5),(8,5),(9,5)]
        self.obstacles = ap.AgentList(self, len(obstacle_positions), Obstacle)
        self.grid.add_agents(self.obstacles, obstacle_positions)  # Place obstacles on the grid

    def step(self):
        self.agents.step()

    def end(self):
        # Print the global trajectory arrays for both agents
        print("\nAgent 1 Trajectory:")
        for step, position in enumerate(agent1_trajectory):
            print(f"Step {step + 1}: Position {position}")

        print("\nAgent 2 Trajectory:")
        for step, position in enumerate(agent2_trajectory):
            print(f"Step {step + 1}: Position {position}")

        # Plotting the trajectories of both agents
        plt.figure()
        for i, agent_trajectory in enumerate([agent1_trajectory, agent2_trajectory]):
            if agent_trajectory:
                trajectory = list(zip(*agent_trajectory))
                plt.plot(trajectory[0], trajectory[1], label=f'Agent {i+1}')
                plt.scatter(*agent_trajectory[-1], color='red')  # Mark the final position

        # Plot obstacles
        for obs in self.obstacles:
            plt.scatter(*self.grid.positions[obs], color='black', marker='x')

        plt.legend()
        plt.grid(True)
        plt.show()


# Create and run the model
parameters = {"steps": 20}
model = MultiAgentModel(parameters)
results = model.run()