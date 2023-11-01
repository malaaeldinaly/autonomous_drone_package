#!/environments/autonomous-drone-env/bin/python3.10

import tkinter as tk
from mavsdk import System, telemetry, mission
import asyncio

async def takeoff():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    await drone.action.arm()
    await drone.action.takeoff()

async def land():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    await drone.action.land()

async def main():
    root = tk.Tk()
    root.title("Drone Control")

    takeoff_button = tk.Button(root, text="Takeoff", command=lambda: asyncio.create_task(takeoff()))
    land_button = tk.Button(root, text="Land", command=lambda: asyncio.create_task(land()))

    takeoff_button.pack()
    land_button.pack()

    root.mainloop()

if name == "main":
    asyncio.run(main())
