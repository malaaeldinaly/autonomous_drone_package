#!/usr/bin/env python3.10

##prints out the path to the currently running Python interpreter executable file. 
import sys
print(sys.executable)


import asyncio
import json
import rospkg
import os  

from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan, MissionItem, MissionPlan)


async def run():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    print_mission_progress_task = asyncio.ensure_future(print_mission_progress(drone))
    ##rospack = rospkg.RosPack()
    ##package_path = rospack.get_path('myPackage')
 
    ##file_path = os.path.join(package_path, 'plans', 'mission_plan.json')
    
    running_tasks = [print_mission_progress_task]
    termination_task = asyncio.ensure_future(observe_is_in_air(drone, running_tasks))
    mission_waypoints = []

    # Load mission waypoints from the JSON file
   ## with open('plans/mission_plan.json', 'r') as json_file:
     ##   mission_waypoints = json.load(json_file)
    try:
        rospack = rospkg.RosPack()
        package_path = rospack.get_path('autonomous_drone_package')


        # Construct the full path to the JSON file
        file_path = os.path.join(package_path, 'plans', 'mission_plan.json')
        ##file_path = "my_package/plans/mission_plan.json"
        
        with open(file_path, 'r') as json_file:
            mission_waypoints = json.load(json_file)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"File path attempted: {file_path}")
    mission_items = []
    for waypoint in mission_waypoints:
        mission_items.append(
            MissionItem(
                waypoint["latitude"],
                waypoint["longitude"],
                waypoint["altitude"],
                waypoint["speed"],
                waypoint["is_fly_through"],
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

    await termination_task


async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")


async def observe_is_in_air(drone, running_tasks):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()

            return


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
