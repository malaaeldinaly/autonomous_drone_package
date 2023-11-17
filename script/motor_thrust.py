#!/usr/bin/env python3.10

import math
G = 9.81  			# Acceleration due to gravity (m/s^2)
# Function to calculate thrust based on mass
def calculate_thrust(mass):
   # Gravity force
   gravity_force = mass * G
   # Additional force to support the mass
   additional_force = 2.0 * gravity_force  # can be adjusted
   # Total thrust per motor
   thrust_per_motor = (gravity_force+additional_force)/4.0
   return thrust_per_motor
# Example mass
mass = 5.0  # kg
# Calculate thrust for each motor
thrust_motor_0 = calculate_thrust(mass)
thrust_motor_1 = calculate_thrust(mass)
thrust_motor_2 = calculate_thrust(mass)
thrust_motor_3 = calculate_thrust(mass)
# Display results
print("Thrust for Motor 0:", thrust_motor_0, "N")
print("Thrust for Motor 1:", thrust_motor_1, "N")
print("Thrust for Motor 2:", thrust_motor_2, "N")
print("Thrust for Motor 3:", thrust_motor_3, "N")