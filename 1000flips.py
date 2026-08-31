def drone_task(flips_per_drone):
    for _ in range(flips_per_drone):
        do_a_flip()

total_flips = 1000
drones = max_drones()
if drones == None:
    drones = 1
if drones < 1:
    drones = 1

flips_per_drone = total_flips // drones
remainder = total_flips % drones

for i in range(drones):
    my_flips = flips_per_drone
    if i < remainder:
        my_flips = my_flips + 1
    
    if i == 0:
        continue
    else:
        spawn_drone(drone_task, my_flips)

main_flips = flips_per_drone
if 0 < remainder:
    main_flips = main_flips + 1

drone_task(main_flips)
