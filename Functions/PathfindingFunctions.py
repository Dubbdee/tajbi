"""
Pathfinding functions for the Walker system.
Provides automatic path calculation between distant waypoints.
"""


def calculate_path_simple(start_x, start_y, start_z, end_x, end_y, end_z):
    """
    Simple pathfinding using linear interpolation.
    Moves diagonally when possible, then straight.
    
    Args:
        start_x, start_y, start_z: Starting coordinates
        end_x, end_y, end_z: Ending coordinates
    
    Returns:
        List of (x, y, z, direction) tuples representing the path from start to end
        Returns empty list if no pathfinding needed (adjacent or different floors)
    """
    # No pathfinding for different floors
    if start_z != end_z:
        return []
    
    # Calculate distance
    dist = max(abs(end_x - start_x), abs(end_y - start_y))
    
    # No pathfinding needed for adjacent squares
    if dist <= 1:
        return []
    
    # Build path using linear interpolation
    path = []
    current_x, current_y = start_x, start_y
    
    while current_x != end_x or current_y != end_y:
        # Calculate next step
        dx = 0 if current_x == end_x else (1 if end_x > current_x else -1)
        dy = 0 if current_y == end_y else (1 if end_y > current_y else -1)
        
        current_x += dx
        current_y += dy
        
        # Determine direction based on movement
        # Direction mapping: 1=North, 2=South, 3=East, 4=West, 5=NE, 6=NW, 7=SE, 8=SW
        if dx == 0 and dy == -1:  # North
            direction = 1
        elif dx == 0 and dy == 1:  # South
            direction = 2
        elif dx == 1 and dy == 0:  # East
            direction = 3
        elif dx == -1 and dy == 0:  # West
            direction = 4
        elif dx == 1 and dy == -1:  # North-East
            direction = 5
        elif dx == -1 and dy == -1:  # North-West
            direction = 6
        elif dx == 1 and dy == 1:  # South-East
            direction = 7
        elif dx == -1 and dy == 1:  # South-West
            direction = 8
        else:  # Shouldn't happen, but use Center as fallback
            direction = 0
        
        path.append((current_x, current_y))
    
    return path


import heapq

def calculate_path_astar(start_x, start_y, end_x, end_y, obstacles=None):
    """
    A* pathfinding algorithm on an empty grid.
    Used when Direction is 0 (Center).
    
    Args:
        start_x, start_y, start_z: Starting coordinates
        end_x, end_y, end_z: Ending coordinates
        obstacles: Set of (x, y) tuples representing blocked coordinates
        
    Returns:
        List of (x, y, z, direction) tuples representing the path
    """
        
    start_node = (start_x, start_y)
    end_node = (end_x, end_y)
    
    # Priority queue for open set: (f_score, x, y)
    open_set = []
    heapq.heappush(open_set, (0, start_x, start_y))
    
    came_from = {}
    g_score = {start_node: 0}
    f_score = {start_node: abs(end_x - start_x) + abs(end_y - start_y)} # Manhattan distance heuristic
    
    while open_set:
        current_f, current_x, current_y = heapq.heappop(open_set)
        current = (current_x, current_y)
        
        if current == end_node:
            # Reconstruct path
            path = []
            while current in came_from:
                prev = came_from[current]
                
                # Calculate offset from prev to current
                dx = current[0] - prev[0]
                dy = current[1] - prev[1]
                
                path.append((dx, dy))
                current = prev
            
            return path[::-1] # Return reversed path
            
        # Generate neighbors (4 directions - No diagonals)
        neighbors = [
            (current_x, current_y - 1), (current_x, current_y + 1), # N, S
            (current_x + 1, current_y), (current_x - 1, current_y)  # E, W
        ]
        
        for neighbor in neighbors:
            # Check if neighbor is in obstacles
            if obstacles and neighbor in obstacles:
                continue
                
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                # Heuristic: Manhattan distance
                h_score = abs(end_x - neighbor[0]) + abs(end_y - neighbor[1])
                f_score[neighbor] = tentative_g_score + h_score
                heapq.heappush(open_set, (f_score[neighbor], neighbor[0], neighbor[1]))
                
    return [] # No path found


def expand_waypoints(waypoints):
    """
    Expand waypoints list by inserting intermediate waypoints
    for distant waypoints (> 1 square apart).
    
    Args:
        waypoints: List of waypoint dictionaries with X, Y, Z, Action, Direction
    
    Returns:
        Expanded list of waypoints with intermediate steps added
    """
    if not waypoints:
        return []
    
    print(f"DEBUG: Expanding {len(waypoints)} waypoints...")
    expanded = []
    
    for i in range(len(waypoints)):
        current_wpt = waypoints[i]
        expanded.append(current_wpt)
        
        # Look ahead to next waypoint
        if i < len(waypoints) - 1:
            next_wpt = waypoints[i + 1]
            
            # Only pathfind between "Stand" waypoints (Action == 0)
            # Skip special actions like Rope, Shovel, Ladder
            if current_wpt['Action'] == 0 and next_wpt['Action'] == 0:
                # Use A* if Direction is 0 (Center/Auto), otherwise use Simple
                if next_wpt['Direction'] == 0:
                     print(f"DEBUG: Calculating A* path from {current_wpt['X']},{current_wpt['Y']} to {next_wpt['X']},{next_wpt['Y']}")
                     path = calculate_path_astar(
                        current_wpt['X'], current_wpt['Y'], current_wpt['Z'],
                        next_wpt['X'], next_wpt['Y'], next_wpt['Z']
                    )
                     print(f"DEBUG: A* path found with {len(path)} steps")
                else:
                    path = calculate_path_simple(
                        current_wpt['X'], current_wpt['Y'], current_wpt['Z'],
                        next_wpt['X'], next_wpt['Y'], next_wpt['Z']
                    )
                
                # Both algorithms return path EXCLUDING start but INCLUDING end.
                # We want to insert everything BEFORE the last point as intermediate waypoints.
                # The last point in 'path' corresponds to 'next_wpt'.
                
                if path:
                    # Update next_wpt Direction to match the last step of the path
                    # This ensures the bot knows how to move to the final waypoint
                    last_step = path[-1]
                    next_wpt['Direction'] = last_step[3]
                    
                    # Insert intermediate waypoints
                    for x, y, z, direction in path[:-1]:
                        intermediate_wpt = {
                            'X': x,
                            'Y': y,
                            'Z': z,
                            'Action': 0,  # Stand action
                            'Direction': direction  # Use calculated direction
                        }
                        expanded.append(intermediate_wpt)
    
    print(f"DEBUG: Expansion complete. Total waypoints: {len(expanded)}")
    return expanded
