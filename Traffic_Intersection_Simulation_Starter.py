import threading
import time

# Weighted round-robin for lanes
lane_weights = [2, 1, 3, 4]  # Adjust as necessary
current_lane = 0
current_weight = lane_weights[current_lane]
lock = threading.Lock()


path_locks = {
    "north_to_south": threading.Lock(),
    "north_to_east": threading.Lock(),
    "north_to_west": threading.Lock(),
    "east_to_north": threading.Lock(),
    "east_to_south": threading.Lock(),
    "east_to_west": threading.Lock(),
    "south_to_east": threading.Lock(),
    "south_to_north": threading.Lock(),
    "south_to_west": threading.Lock(),
    "west_to_north": threading.Lock(),
    "west_to_east": threading.Lock(),
    "west_to_south": threading.Lock(),
}


def get_next_lane():
    global current_lane, current_weight
    with lock:
        if current_weight > 0:
            current_weight -= 1
        else:
            current_lane = (current_lane + 1) % len(lane_weights)
            current_weight = lane_weights[current_lane] - 1
        return current_lane


def get_path_lock(vehicle):
    paths = {
        "straight": ["north_to_south", "east_to_west", "south_to_north", "west_to_east"],
        "left": ["north_to_east", "east_to_south", "south_to_west", "west_to_north"],
        "right": ["north_to_west", "east_to_north", "south_to_east", "west_to_south"]
    }
    return path_locks[paths[vehicle.route][vehicle.lane]]


def can_enter_intersection(vehicle):
    if vehicle.vehicle_type == "Emergency":
        return True
    path_lock = get_path_lock(vehicle)
    return not path_lock.locked()


def enter_intersection(vehicle):
    path_lock = get_path_lock(vehicle)
    path_lock.acquire()


def exit_intersection(vehicle):
    path_lock = get_path_lock(vehicle)
    path_lock.release()


def is_lane_turn(vehicle):
    with lock:
        return vehicle.vehicle_type == "Emergency" or vehicle.lane == current_lane

class Vehicle(threading.Thread):
    def __init__(self, vehicle_id, vehicle_type, lane, route, crossing_time):
        threading.Thread.__init__(self)
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.lane = lane
        self.route = route
        self.crossing_time = crossing_time

    def run(self):
        if self.vehicle_type == "Emergency":
            enter_intersection(self)
            print(f"Emergency Vehicle {self.vehicle_id} is crossing {self.route}.")
            time.sleep(self.crossing_time)
            exit_intersection(self)
            print(f"Emergency Vehicle {self.vehicle_id} has exited the intersection.")
            return

       
        while not (can_enter_intersection(self) and is_lane_turn(self)):
            time.sleep(0.1)

        
        enter_intersection(self)
        print(f"Vehicle {self.vehicle_id} from lane {self.lane} is crossing {self.route}.")
        time.sleep(self.crossing_time)  
        exit_intersection(self)
        print(f"Vehicle {self.vehicle_id} has exited the intersection.")
        get_next_lane()  

if __name__ == "__main__":
    vehicles = [
        Vehicle(1, "Regular", 0, "straight", 2),
        Vehicle(2, "Regular", 1, "straight", 1),
        Vehicle(3, "Regular", 2, "left", 3),
        Vehicle(4, "Emergency", 3, "right", 2),
        Vehicle(5, "Regular", 0, "left", 1),
        Vehicle(6, "Emergency", 1, "right", 3),
        Vehicle(7, "Regular", 2, "straight", 1),
        Vehicle(8, "Regular", 3, "left", 2),
        Vehicle(9, "Regular", 0, "right", 3),
        Vehicle(10, "Regular", 1, "left", 2)
    ]
    for v in vehicles:
        v.start()
    for v in vehicles:
        v.join()
    print("All vehicles have completed their crossings.")
