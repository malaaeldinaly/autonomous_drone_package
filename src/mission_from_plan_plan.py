#!/usr/bin/env python3.10

import sys
print(sys.executable)

import asyncio
import json
import rospkg
import os
import time  # Import the time module

from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    print_mission_progress_task = asyncio.ensure_future(print_mission_progress(drone))
    
    try:
        # Get the path to the current package directory
        rospack = rospkg.RosPack()
        package_path = rospack.get_path('autonomous_drone_package')

        # Construct the full path to the plan file
        file_path = os.path.join(package_path, 'plans', 'debrecen_tour.plan')
        ##file_path = "my_package/plans/mission_plan.plan"


        with open(file_path, 'r') as json_file:
            mission_data = json.load(json_file)

        mission_items = []
        for waypoint in mission_data["mission"]["items"]:
            mission_items.append(
                MissionItem(
                    waypoint["params"][4] or 0.0,
                    waypoint["params"][5] or 0.0,
                    waypoint["params"][3] or 0.0,
                    waypoint["params"][1] or 0.0,
                    True,  # Assuming all waypoints are fly-through
                    float('nan'),
                    float('nan'),
                    MissionItem.CameraAction.NONE,
                    float('nan'),
                    float('nan'),
                    float('nan'),
                    float('nan'),
                    float('nan')
                )
            )

        mission_plan = MissionPlan(mission_items)

        await drone.mission.set_return_to_launch_after_mission(True)

        print("-- Uploading mission")
        await drone.mission.upload_mission(mission_plan)

        print("Waiting for drone to have a global position estimate...")
        async for health in drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print("-- Global position estimate OK")
                break

        print("-- Arming")
        await drone.action.arm()

        print("-- Starting mission")
        await drone.mission.start_mission()

        await execute_mission_with_delays(drone, print_mission_progress_task)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")

async def execute_mission_with_delays(drone, print_mission_progress_task):
    async for mission_progress in drone.mission.mission_progress():
        current_waypoint = mission_progress.current - 1  # Adjust for 0-based indexing
        print(f"Reached Waypoint {current_waypoint + 1}")
        print("Waiting for 3 seconds...")
        await asyncio.sleep(3)      # Wait for 3 seconds
        print("Continuing to the next waypoint")

    # Ensure that the print_mission_progress_task is completed before finishing
    await print_mission_progress_task

if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
