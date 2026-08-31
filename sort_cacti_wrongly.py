def prepare_soil():
    if get_ground_type() == Grounds.Grassland:
        till()

def move_to_x(target):
    while get_pos_x() < target:
        move(East)
    while get_pos_x() > target:
        move(West)

def move_to_y(target):
    while get_pos_y() < target:
        move(North)
    while get_pos_y() > target:
        move(South)

def move_to_column_bottom(x):
    move_to_x(x)
    while get_pos_y() > 0:
        move(South)

def move_to_column_top(x):
    move_to_x(x)
    size = get_world_size()
    while get_pos_y() < size - 1:
        move(North)

def split_columns(count):
    size = get_world_size()
    if count < 1:
        count = 1
    if count > size:
        count = size
    result = []
    base = size // count
    remainder = size % count
    start = 0
    for i in range(count):
        width = base
        if i < remainder:
            width += 1
        end = start + width - 1
        result.append((start, end))
        start = end + 1
    return result

def traverse_columns(start_x, end_x, action_callback):
    size = get_world_size()
    width = end_x - start_x + 1
    is_odd_width = (width % 2 != 0)

    def run_pass(going_up_start):
        going_up = going_up_start
        for i in range(width):
            x = start_x + i
            if going_up:
                for y in range(size):
                    action_callback(x, y)
                    if y < size - 1:
                        move(North)
            else:
                for y in range(size - 1, -1, -1):
                    action_callback(x, y)
                    if y > 0:
                        move(South)
            if i < width - 1:
                move(East)
                going_up = not going_up

    curr_x = get_pos_x()
    curr_y = get_pos_y()

    if curr_x >= start_x and curr_x <= end_x:
        start_at_top = (curr_y >= size // 2)
    else:
        move_to_column_bottom(start_x)
        start_at_top = False

    if start_at_top:
        move_to_column_top(start_x)
        run_pass(False)
        if is_odd_width:
            move_to_column_bottom(start_x)
            run_pass(True)
    else:
        move_to_column_bottom(start_x)
        run_pass(True)
        if is_odd_width:
            move_to_column_top(start_x)
            run_pass(False)

def inverted_cactus_swap():
    value = measure()
    if value == None:
        return False
    x = get_pos_x()
    y = get_pos_y()
    size = get_world_size()
    if x > 0:
        other = measure(West)
        if other != None and value > other:
            swap(West)
            return True
    if y > 0:
        other = measure(South)
        if other != None and value > other:
            swap(South)
            return True
    if x < size - 1:
        other = measure(East)
        if other != None and value < other:
            swap(East)
            return True
    if y < size - 1:
        other = measure(North)
        if other != None and value < other:
            swap(North)
            return True
    return False

def inverted_cactus_is_sorted():
    value = measure()
    if value == None:
        return True
    x = get_pos_x()
    y = get_pos_y()
    size = get_world_size()
    if x > 0:
        other = measure(West)
        if other != None and value > other:
            return False
    if y > 0:
        other = measure(South)
        if other != None and value > other:
            return False
    if x < size - 1:
        other = measure(East)
        if other != None and value < other:
            return False
    if y < size - 1:
        other = measure(North)
        if other != None and value < other:
            return False
    return True

def ensure_inverted_cactus(start_x, end_x):
    def action(x, y):
        if get_entity_type() != Entities.Cactus:
            prepare_soil()
            plant(Entities.Cactus)
        inverted_cactus_swap()
    traverse_columns(start_x, end_x, action)

def check_inverted_cactus(start_x, end_x):
    field_ready = [True]
    def action(x, y):
        if get_entity_type() != Entities.Cactus:
            prepare_soil()
            plant(Entities.Cactus)
        if not can_harvest() or not inverted_cactus_is_sorted():
            field_ready[0] = False
            inverted_cactus_swap()
    traverse_columns(start_x, end_x, action)
    return field_ready[0]

def drone_cactus_loop(start_x, end_x):
    while True:
        ensure_inverted_cactus(start_x, end_x)
        while True:
            if check_inverted_cactus(start_x, end_x):
                break
        move_to_column_bottom(start_x)
        harvest()

def main():
    clear()
    size = get_world_size()
    drones = max_drones()
    if drones == None:
        drones = 1
    if drones < 1:
        drones = 1

    ranges = split_columns(drones)
    for i in range(1, len(ranges)):
        r = ranges[i]
        spawn_drone(drone_cactus_loop, r[0], r[1])
    
    r0 = ranges[0]
    drone_cactus_loop(r0[0], r0[1])

main()
