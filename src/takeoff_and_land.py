#!/usr/bin/env python3.10

# Import necessary libraries
import sys  # Access system-specific parameters and functions
import asyncio  # Asynchronous I/O, event loop, coroutines
from mavsdk import System  # Import MAVSDK's System module

# Print the path to the currently running Python interpreter executable file
print(sys.executable)

# Asynchronous function to control the drone
async def run():
    # Initialize the drone's system
    drone = System()

    # Connect to the drone using mavlink system address
    await drone.connect(system_address="udp://:14540")

    # Create a task to print the status text
    status_text_task = asyncio.ensure_future(print_status_text(drone))

    # Wait for the drone to establish a connection
    print("Waiting for the drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to the drone!")
            break

    # Wait for the drone to have a reliable global position estimate
    print("Waiting for the drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate is OK")
            break

    # Arm the drone
    print("-- Arming the drone")
    await drone.action.arm()

    # Initiate the takeoff sequence
    print("-- Taking off")
    await drone.action.takeoff()

    # Maintain the drone in the air for 20 seconds
    await asyncio.sleep(20)

    # Instruct the drone to land
    print("-- Landing")
    await drone.action.land()

    # Cancel the status text task
    status_text_task.cancel()

# Asynchronous function to print status text of the drone
async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return

# Run the asynchronous event loop if the script is executed directly
if __name__ == "__main__":
    asyncio.run(run())  # Run the main async function
