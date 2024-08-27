from flask import Flask, request, jsonify
from aStarParametrizada import run_multi_agent_model

app = Flask(__name__)

@app.route('/compute-paths', methods=['POST'])
def compute_paths():
    data = request.json
    
    agent1_start = (int(data['posicionAgenteUno']['x']), int(data['posicionAgenteUno']['y']))
    agent1_goal = (int(data['destinoAgenteUno']['x']), int(data['destinoAgenteUno']['y']))
    agent2_start = (int(data['posicionAgenteDos']['x']), int(data['posicionAgenteDos']['y']))
    agent2_goal = (int(data['destinoAgenteDos']['x']), int(data['destinoAgenteDos']['y']))
    
    grid_shape = (int(data['matrizX']), int(data['matrizY']))
    
    obstacle_positions = [(int(obs['x']), int(obs['y'])) for obs in data['obstaculos']]
    
    steps = data.get('steps', 30) 
    
    agent1_trajectory, agent2_trajectory = run_multi_agent_model(
        grid_shape, 
        [agent1_start, agent2_start], 
        [agent1_goal, agent2_goal], 
        obstacle_positions, 
        steps
    )

    print("Agent 1 Trajectory:")
    for step, position in enumerate(agent1_trajectory):
        print(f"Step {step}: Position {position}")

    print("\nAgent 2 Trajectory:")
    for step, position in enumerate(agent2_trajectory):
        print(f"Step {step}: Position {position}")

    response = {
        'agent1_path': [list(pos) for pos in agent1_trajectory],
        'agent2_path': [list(pos) for pos in agent2_trajectory]
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
