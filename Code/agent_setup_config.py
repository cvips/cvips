"""
Town10HD Scenario 01

veh1_bp = self.blueprint_library.filter("model3")[0]
veh1_bp.set_attribute('role_name', 'hero' )
veh1_transform = carla.Transform(carla.Location(x=-49.382700, y=-31.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
veh1 = self.world.spawn_actor(veh1_bp, veh1_transform)
veh1.set_autopilot(True)

# breakpoint()
# veh2_loc =  # 5 (vehicle length) + 2 (gap)
veh2_transform = carla.Transform(carla.Location(x=-49.642700, y=-41.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
veh2_bp = self.blueprint_library.filter("model3")[0]  # Use the same blueprint or choose another vehicle type.
veh2_bp.set_attribute('role_name', 'second_vehicle')
veh2 = self.world.spawn_actor(veh2_bp, veh2_transform)
veh2.set_autopilot(True)

veh3_bp = self.blueprint_library.filter("model3")[0]
veh3_bp.set_attribute('role_name', 'fourth_vehicle' )
veh3_transform = carla.Transform(carla.Location(x=-90.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
veh3 = self.world.spawn_actor(veh3_bp, veh3_transform)
veh3.set_autopilot(True)
veh4_transform = carla.Transform(carla.Location(x=-80.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
veh4_bp = self.blueprint_library.filter("model3")[0] 
veh4_bp.set_attribute('role_name', 'fourth_vehicle')
veh4 = self.world.spawn_actor(veh4_bp, veh4_transform)
veh4.set_autopilot(True)


camera_positions_infra1 = {
    'Camera_Front':       carla.Transform(carla.Location(x=-65.000000, y=5.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)),
    'Camera_FrontRight': carla.Transform(carla.Location(x=-65.000000, y=5.000000, z=4.000000), carla.Rotation(pitch=0, yaw=55, roll=0)),
    'Camera_FrontLeft':  carla.Transform(carla.Location(x=-65.000000, y=5.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-55, roll=0)),
    'Camera_Back':        carla.Transform(carla.Location(x=-65.000000, y=5.000000, z=4.000000), carla.Rotation(pitch=0, yaw=180, roll=0)),
    'Camera_BackRight':  carla.Transform(carla.Location(x=-65.000000, y=5.000000, z=4.000000), carla.Rotation(pitch=0, yaw=110, roll=0)),
    'Camera_BackLeft':   carla.Transform(carla.Location(x=-65.000000, y=5.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-110, roll=0))
}

camera_positions_infra2 = {
    'Camera_Front':       carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)),
    'Camera_FrontRight': carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=55, roll=0)),
    'Camera_FrontLeft':  carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-55, roll=0)),
    'Camera_Back':        carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=180, roll=0)),
    'Camera_BackRight':  carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=110, roll=0)),
    'Camera_BackLeft':   carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-110, roll=0))
}








"""

"""
Town10HD Scenario 02

veh1_bp = self.blueprint_library.filter("model3")[0]
veh1_bp.set_attribute('role_name', 'hero' )
veh1_transform = carla.Transform(carla.Location(x=-49.382700, y=-31.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
veh1 = self.world.spawn_actor(veh1_bp, veh1_transform)
veh1.set_autopilot(True)

# breakpoint()
# veh2_loc =  # 5 (vehicle length) + 2 (gap)
veh2_transform = carla.Transform(carla.Location(x=-49.642700, y=-41.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
veh2_bp = self.blueprint_library.filter("model3")[0]  # Use the same blueprint or choose another vehicle type.
veh2_bp.set_attribute('role_name', 'second_vehicle')
veh2 = self.world.spawn_actor(veh2_bp, veh2_transform)
veh2.set_autopilot(True)

veh3_bp = self.blueprint_library.filter("model3")[0]
veh3_bp.set_attribute('role_name', 'fourth_vehicle' )
veh3_transform = carla.Transform(carla.Location(x=-90.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
veh3 = self.world.spawn_actor(veh3_bp, veh3_transform)
veh3.set_autopilot(True)
veh4_transform = carla.Transform(carla.Location(x=-80.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
veh4_bp = self.blueprint_library.filter("model3")[0] 
veh4_bp.set_attribute('role_name', 'fourth_vehicle')
veh4 = self.world.spawn_actor(veh4_bp, veh4_transform)
veh4.set_autopilot(True)


"""



"""
Town10HD Scenario 03

veh1_bp = self.blueprint_library.filter("model3")[0]
veh1_bp.set_attribute('role_name', 'hero' )
veh1_transform = carla.Transform(carla.Location(x=-49.382700, y=-31.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
veh1 = self.world.spawn_actor(veh1_bp, veh1_transform)
veh1.set_autopilot(True)

# breakpoint()
# veh2_loc =  # 5 (vehicle length) + 2 (gap)
veh2_transform = carla.Transform(carla.Location(x=-49.642700, y=-41.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
veh2_bp = self.blueprint_library.filter("model3")[0]  # Use the same blueprint or choose another vehicle type.
veh2_bp.set_attribute('role_name', 'second_vehicle')
veh2 = self.world.spawn_actor(veh2_bp, veh2_transform)
veh2.set_autopilot(True)

veh3_bp = self.blueprint_library.filter("model3")[0]
veh3_bp.set_attribute('role_name', 'fourth_vehicle' )
veh3_transform = carla.Transform(carla.Location(x=-90.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
veh3 = self.world.spawn_actor(veh3_bp, veh3_transform)
veh3.set_autopilot(True)
veh4_transform = carla.Transform(carla.Location(x=-80.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
veh4_bp = self.blueprint_library.filter("model3")[0] 
veh4_bp.set_attribute('role_name', 'fourth_vehicle')
veh4 = self.world.spawn_actor(veh4_bp, veh4_transform)
veh4.set_autopilot(True)


"""




"""
Town10HD Scenario 04

veh1_bp = self.blueprint_library.filter("model3")[0]
veh1_bp.set_attribute('role_name', 'hero' )
veh1_transform = carla.Transform(carla.Location(x=-49.382700, y=-31.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
veh1 = self.world.spawn_actor(veh1_bp, veh1_transform)
veh1.set_autopilot(True)

# breakpoint()
# veh2_loc =  # 5 (vehicle length) + 2 (gap)
veh2_transform = carla.Transform(carla.Location(x=-49.642700, y=-41.353889, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.432304, roll=0.000000))
veh2_bp = self.blueprint_library.filter("model3")[0]  # Use the same blueprint or choose another vehicle type.
veh2_bp.set_attribute('role_name', 'second_vehicle')
veh2 = self.world.spawn_actor(veh2_bp, veh2_transform)
veh2.set_autopilot(True)

veh3_bp = self.blueprint_library.filter("model3")[0]
veh3_bp.set_attribute('role_name', 'fourth_vehicle' )
veh3_transform = carla.Transform(carla.Location(x=-90.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
veh3 = self.world.spawn_actor(veh3_bp, veh3_transform)
veh3.set_autopilot(True)
veh4_transform = carla.Transform(carla.Location(x=-80.11, y=27.71, z=0.600000), carla.Rotation(pitch=0.000000, yaw=0.000000, roll=0.000000))
veh4_bp = self.blueprint_library.filter("model3")[0] 
veh4_bp.set_attribute('role_name', 'fourth_vehicle')
veh4 = self.world.spawn_actor(veh4_bp, veh4_transform)
veh4.set_autopilot(True)


"""



# TODO: Town 05

"""
Town05 Scenario 01

veh1_bp = self.blueprint_library.filter("model3")[0]
veh1_bp.set_attribute('role_name', 'hero' )
veh1_transform = carla.Transform(carla.Location(x=0.7, y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000))
veh1 = self.world.spawn_actor(veh1_bp, veh1_transform)
veh1.set_autopilot(True)

# breakpoint()
# veh2_loc =  # 5 (vehicle length) + 2 (gap)
veh2_transform = carla.Transform(carla.Location(x=-10,y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000))
veh2_bp = self.blueprint_library.filter("model3")[0]  # Use the same blueprint or choose another vehicle type.
veh2_bp.set_attribute('role_name', 'second_vehicle')
veh2 = self.world.spawn_actor(veh2_bp, veh2_transform)
veh2.set_autopilot(True)

veh3_bp = self.blueprint_library.filter("model3")[0]
veh3_bp.set_attribute('role_name', 'third_vehicle' )
veh3_transform = carla.Transform(carla.Location(x=-54.74, y=-41.50, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.000000, roll=0.000000))
veh3 = self.world.spawn_actor(veh3_bp, veh3_transform)
veh3.set_autopilot(True)


veh4_transform = carla.Transform(carla.Location(x=-43.60, y=53.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.000000, roll=0.000000))
veh4_bp = self.blueprint_library.filter("model3")[0] 
veh4_bp.set_attribute('role_name', 'fourth_vehicle')
veh4 = self.world.spawn_actor(veh4_bp, veh4_transform)
veh4.set_autopilot(True)



camera_positions_infra1 = {
    'Camera_Front':      carla.Transform(carla.Location(x=-60.000000, y=-90.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)),
    'Camera_FrontRight': carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=55, roll=0)),
    'Camera_FrontLeft':  carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-55, roll=0)),
    'Camera_Back':       carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=180, roll=0)),
    'Camera_BackRight':  carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=110, roll=0)),
    'Camera_BackLeft':   carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-110, roll=0))
}

camera_positions_infra2 = {
    'Camera_Front':      carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)),
    'Camera_FrontRight': carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=55, roll=0)),
    'Camera_FrontLeft':  carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-55, roll=0)),
    'Camera_Back':       carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=180, roll=0)),
    'Camera_BackRight':  carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=110, roll=0)),
    'Camera_BackLeft':   carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-110, roll=0))
}

"""



"""
Town05 Scenario 02

veh1_bp = self.blueprint_library.filter("model3")[0]
veh1_bp.set_attribute('role_name', 'hero' )
veh1_transform = carla.Transform(carla.Location(x=0.7, y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000))
veh1 = self.world.spawn_actor(veh1_bp, veh1_transform)
veh1.set_autopilot(True)

# breakpoint()
# veh2_loc =  # 5 (vehicle length) + 2 (gap)
veh2_transform = carla.Transform(carla.Location(x=-10,y=-4.49, z=0.600000), carla.Rotation(pitch=0.000000, yaw=180, roll=0.000000))
veh2_bp = self.blueprint_library.filter("model3")[0]  # Use the same blueprint or choose another vehicle type.
veh2_bp.set_attribute('role_name', 'second_vehicle')
veh2 = self.world.spawn_actor(veh2_bp, veh2_transform)
veh2.set_autopilot(True)

veh3_bp = self.blueprint_library.filter("model3")[0]
veh3_bp.set_attribute('role_name', 'third_vehicle' )
veh3_transform = carla.Transform(carla.Location(x=-54.74, y=-41.50, z=0.600000), carla.Rotation(pitch=0.000000, yaw=90.000000, roll=0.000000))
veh3 = self.world.spawn_actor(veh3_bp, veh3_transform)
veh3.set_autopilot(True)


veh4_transform = carla.Transform(carla.Location(x=-43.60, y=53.76, z=0.600000), carla.Rotation(pitch=0.000000, yaw=270.000000, roll=0.000000))
veh4_bp = self.blueprint_library.filter("model3")[0] 
veh4_bp.set_attribute('role_name', 'fourth_vehicle')
veh4 = self.world.spawn_actor(veh4_bp, veh4_transform)
veh4.set_autopilot(True)



camera_positions_infra1 = {
    'Camera_Front':      carla.Transform(carla.Location(x=-60.000000, y=-90.00000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)),
    'Camera_FrontRight': carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=55, roll=0)),
    'Camera_FrontLeft':  carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-55, roll=0)),
    'Camera_Back':       carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=180, roll=0)),
    'Camera_BackRight':  carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=110, roll=0)),
    'Camera_BackLeft':   carla.Transform(carla.Location(x=-60.000000, y=-90.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-110, roll=0))
}

camera_positions_infra2 = {
    'Camera_Front':      carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=0, roll=0)),
    'Camera_FrontRight': carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=55, roll=0)),
    'Camera_FrontLeft':  carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-55, roll=0)),
    'Camera_Back':       carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=180, roll=0)),
    'Camera_BackRight':  carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=110, roll=0)),
    'Camera_BackLeft':   carla.Transform(carla.Location(x=-36.000000, y=10.000000, z=4.000000), carla.Rotation(pitch=0, yaw=-110, roll=0))
}

"""












