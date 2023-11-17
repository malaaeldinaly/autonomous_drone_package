#!/usr/bin/env python3.10

import sys
import asyncio
import json
import os
import rospkg
import time
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from math import radians, sin, cos, sqrt, atan2

# Print the path to the currently running Python interpreter executable file
print(sys.executable)

plan_file_name = "debrecen_tour_plan.json" 

async def run():
    # Connect to the drone
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    
    # Wait for the drone to establish a connection
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    # Print mission progress while running the mission
    print_mission_progress_task = asyncio.ensure_future(print_mission_progress(drone))

    # Ensure tasks are properly canceled upon mission completion or termination
    running_tasks = [print_mission_progress_task]
    termination_task = asyncio.ensure_future(observe_is_in_air(drone, running_tasks))

    # Load mission waypoints from a JSON file
    mission_waypoints = load_mission_waypoints()

    # Convert mission waypoints to MissionItems
    mission_items = create_mission_items(mission_waypoints)

    # Create a MissionPlan from the MissionItems
    mission_plan = MissionPlan(mission_items)

    # Set the drone to return to launch after completing the mission
    await drone.mission.set_return_to_launch_after_mission(True)

    # Upload the mission to the drone
    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    # Wait for the drone to have a global position estimate
    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    # Arm the drone
    print("-- Arming")
    await drone.action.arm()

    # Start the mission
    print("-- Starting mission")
    await drone.mission.start_mission()
    print("---------------------------------------------------")

    # Initialize variables for time and distance tracking
    total_time = 0.0
    total_distance = 0.0
    previous_position = await get_drone_position(drone)


    # Iterate over mission items and record time, and distance taken for each
    for i, mission_item in enumerate(mission_items):
        start_time = time.time()
        async for mission_progress in drone.mission.mission_progress():
            if mission_progress.current == i + 1:
                await drone.mission.pause_mission()
                # Calculate and print the time taken for the current mission item                
                end_time = time.time()
                time_taken = end_time - start_time
                total_time+=time_taken
                print(f"Mission progress: {i + 1}/{len(mission_items)}")
                print(f"Time taken for Mission Item [{i + 1}]: {time_taken/60:.0f}:{time_taken%60:.0f}")
                # Calculate and print the distance covered between consecutive mission items
                current_position = await get_drone_position(drone)
                if previous_position is not None and current_position is not None:
                    distance_between_waypoints = calculate_distance(
                        previous_position, current_position
                    )
                    total_distance += distance_between_waypoints
                    print(f"Distance covered between Mission Item [{i}] and [{i + 1}]: {distance_between_waypoints/1000:.2f} kilometers")

                print(f"Waiting for 10 Seconds to descend the shipment")
                print("---------------------------------------------------")
                #await asyncio.sleep(120)   # Wait for descending the package 
                await asyncio.sleep(10)     # Just simulating the waiting time    
                # Update the previous position
                previous_position = current_position

                # Resume the mission
                await drone.mission.start_mission()
                break

    print(f"Total Time of the Trip: {total_time/60:.0f} minutes, and {total_time%60:.0f} seconds")
    print(f"Total Distance Covered: {total_distance/1000:.2f} kilometers")

    await termination_task

async def print_mission_progress(drone):
    # Print mission progress
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")

def load_mission_waypoints():
    try:
        # Get the path to the JSON file
        package_path = get_package_path('autonomous_drone_package')
        file_path = os.path.join(package_path, 'plans', plan_file_name)
        #file_path = "package_path/plans/plan_file_name"

        # Load mission waypoints from the JSON file
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"File path attempted: {file_path}")
        return []

def create_mission_items(mission_waypoints):
    # Convert mission waypoints to MissionItems
    mission_items = []
    for waypoint in mission_waypoints:
        mission_items.append(MissionItem(
            waypoint["latitude"],   # Latitude of the waypoint
            waypoint["longitude"],  # Longitude of the waypoint
            waypoint["altitude"],   # Altitude of the waypoint
            waypoint["speed"],      # Speed at which the drone should reach the waypoint
            waypoint["is_fly_through"],     # Flag indicating whether the drone should fly through the waypoint without stopping
            float('nan'),   # Camera action: Camera gimbal pitch
            float('nan'),   # Camera action: Camera gimbal yaw
            MissionItem.CameraAction.NONE,  # Camera action: No specific camera action for this waypoint
            float('nan'),   # Camera action: Loiter time
            float('nan'),   # Camera action: Camera photo interval
            float('nan'),   # Camera action: Camera photo count
            float('nan'),   # Camera action: Camera focus
            float('nan')    # Camera action: Camera zoom level
        ))
    return mission_items

def get_package_path(package_name):
    # Get the path to the specified ROS package
    rospack = rospkg.RosPack()
    return rospack.get_path(package_name)

async def observe_is_in_air(drone, running_tasks):
    # Monitor whether the drone is flying and return after landing
    was_in_air = False
    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            # Cancel tasks and shutdown the async event loop
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()
            return

async def get_drone_position(drone):
    # Get the current position of the drone
    async for position in drone.telemetry.position():
        return position.latitude_deg, position.longitude_deg


def calculate_distance(point1, point2):
    # Haversine formula to calculate the distance between two points
    lat1, lon1 = radians(point1[0]), radians(point1[1])
    lat2, lon2 = radians(point2[0]), radians(point2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Radius of the Earth in meters
    radius = 6371000

    # Calculate the distance
    distance = radius * c

    return distance


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
