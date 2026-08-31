TARGET_RESOURCE = 7
TARGET_COST = None

RESOURCE_CONFIG = {
	0: (Entities.Grass, False, "normal", "max", False),
	1: (Entities.Tree, False, "wood", "max", False),
	2: (Entities.Bush, False, "wood", "max", False),
	3: (Entities.Carrot, True, "normal", "max", False),
	4: (Entities.Pumpkin, True, "pumpkin", "max", False),
	5: (Entities.Cactus, True, "cactus", "max", False),
	6: ("Mixed", False, "mixed", "max", False),
	7: (Entities.Dinosaur, False, "dinosaur", None, False),
	8: ("Maze", False, "maze", None, False),
	9: (Entities.Carrot, True, "normal", "max", True)
}

ENTITY, NEEDS_SOIL, MODE, WORKERS, FERTILIZE = RESOURCE_CONFIG[TARGET_RESOURCE]
PUMPKIN_PASSES = 2

def prepare_soil():
	if get_ground_type() == Grounds.Grassland:
		till()

def get_worker_count():
	if WORKERS == "max":
		count = max_drones()
		if count == None:
			return 1
		return count
	if WORKERS == None:
		return 1
	return WORKERS

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

def plant_crop(crop):
	if crop == Entities.Carrot or NEEDS_SOIL:
		prepare_soil()
	plant(crop)

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

def traverse_rows_offset(action_callback):
	size = get_world_size()
	move_to_column_bottom(0)
	going_right = True
	for y in range(size):
		if going_right:
			for x in range(size):
				action_callback(x, y)
				if x < size - 1:
					move(East)
		else:
			for x in range(size - 1, -1, -1):
				action_callback(x, y)
				if x > 0:
					move(West)
		if y < size - 1:
			move(North)
			going_right = not going_right

def cactus_swap(core_start_x, core_end_x):
	value = measure()
	if value == None:
		return False
	x = get_pos_x()
	y = get_pos_y()
	size = get_world_size()
	if x > 0:
		other = measure(West)
		if other != None and value < other:
			swap(West)
			return True
	if y > 0:
		other = measure(South)
		if other != None and value < other:
			swap(South)
			return True
	if x < size - 1:
		other = measure(East)
		if other != None and value > other:
			swap(East)
			return True
	if y < size - 1:
		other = measure(North)
		if other != None and value > other:
			swap(North)
			return True
	return False

def cactus_is_sorted():
	value = measure()
	if value == None:
		return True
	x = get_pos_x()
	y = get_pos_y()
	size = get_world_size()
	if x > 0:
		other = measure(West)
		if other != None and value < other:
			return False
	if y > 0:
		other = measure(South)
		if other != None and value < other:
			return False
	if x < size - 1:
		other = measure(East)
		if other != None and value > other:
			return False
	if y < size - 1:
		other = measure(North)
		if other != None and value > other:
			return False
	return True

def ensure_cactus_planted_and_sorted(core_start_x, core_end_x):
	if get_entity_type() != Entities.Cactus:
		prepare_soil()
		plant(Entities.Cactus)
	if can_harvest():
		cactus_swap(core_start_x, core_end_x)

def support_drone_loop(start_x, end_x, core_start_x, core_end_x):
	def plant_action(x, y):
		ensure_cactus_planted_and_sorted(core_start_x, core_end_x)
	def check_action(x, y):
		ensure_cactus_planted_and_sorted(core_start_x, core_end_x)
		if can_harvest():
			cactus_swap(core_start_x, core_end_x)
	while True:
		traverse_columns(start_x, end_x, plant_action)
		while True:
			traverse_columns(start_x, end_x, check_action)

def primary_drone_loop(core_start_x, core_end_x):
	def plant_action(x, y):
		ensure_cactus_planted_and_sorted(core_start_x, core_end_x)
	size = get_world_size()
	while True:
		traverse_rows_offset(plant_action)
		while True:
			field_ready = [True]
			def fix_and_scan_action(x, y):
				ensure_cactus_planted_and_sorted(core_start_x, core_end_x)
				if not can_harvest() or not cactus_is_sorted():
					field_ready[0] = False
					cactus_swap(core_start_x, core_end_x)
			traverse_rows_offset(fix_and_scan_action)
			if field_ready[0]:
				break
		move_to_column_bottom(0)
		harvest()

def start_cactus():
	count = get_worker_count()
	size = get_world_size()
	if count <= 1:
		primary_drone_loop(0, size - 1)
		return
	support_count = count - 1
	ranges = split_columns(support_count)
	for r in ranges:
		spawn_drone(support_drone_loop, r[0], r[1], 0, size - 1)
	primary_drone_loop(0, size - 1)

def farm_normal_zone(start_x, end_x, crop, use_fertilizer):
	def init_action(x, y):
		plant_crop(crop)
	traverse_columns(start_x, end_x, init_action)
	while True:
		def normal_action(x, y):
			if can_harvest():
				harvest()
				plant_crop(crop)
				if use_fertilizer:
					use_item(Items.Fertilizer)
		traverse_columns(start_x, end_x, normal_action)

def start_normal():
	count = get_worker_count()
	ranges = split_columns(count)
	for i in range(1, len(ranges)):
		r = ranges[i]
		spawn_drone(farm_normal_zone, r[0], r[1], ENTITY, FERTILIZE)
	r0 = ranges[0]
	farm_normal_zone(0, r0[1], ENTITY, FERTILIZE)

def wood_type():
	x = get_pos_x()
	y = get_pos_y()
	if (x + y) % 2 == 0:
		return Entities.Tree
	return Entities.Bush

def farm_wood_zone(start_x, end_x):
	def wood_action(x, y):
		e_type = get_entity_type()
		w_type = wood_type()
		if e_type != w_type:
			if e_type != None:
				harvest()
			plant(w_type)
	traverse_columns(start_x, end_x, wood_action)
	while True:
		def wood_harvest_action(x, y):
			if can_harvest():
				harvest()
				plant(wood_type())
		traverse_columns(start_x, end_x, wood_harvest_action)

def start_wood():
	count = get_worker_count()
	ranges = split_columns(count)
	for i in range(1, len(ranges)):
		r = ranges[i]
		spawn_drone(farm_wood_zone, r[0], r[1])
	r0 = ranges[0]
	farm_wood_zone(0, r0[1])

def mixed_type():
	x = get_pos_x()
	y = get_pos_y()
	value = (x + y) % 4
	if value == 0:
		return Entities.Tree
	if value == 1:
		return Entities.Carrot
	if value == 2:
		return Entities.Bush
	return Entities.Grass

def farm_mixed_zone(start_x, end_x):
	def mixed_action(x, y):
		e_type = get_entity_type()
		m_type = mixed_type()
		if e_type != m_type:
			if e_type != None:
				harvest()
			plant_crop(m_type)
	traverse_columns(start_x, end_x, mixed_action)
	while True:
		def mixed_harvest_action(x, y):
			if can_harvest():
				harvest()
				plant_crop(mixed_type())
		traverse_columns(start_x, end_x, mixed_harvest_action)

def start_mixed():
	count = get_worker_count()
	ranges = split_columns(count)
	for i in range(1, len(ranges)):
		r = ranges[i]
		spawn_drone(farm_mixed_zone, r[0], r[1])
	r0 = ranges[0]
	farm_mixed_zone(0, r0[1])

def pumpkin_zone(start_x, end_x):
	while True:
		def pumpkin_plant_action(x, y):
			if get_entity_type() != Entities.Pumpkin:
				prepare_soil()
				plant(Entities.Pumpkin)
		traverse_columns(start_x, end_x, pumpkin_plant_action)

def pumpkin_primary_scan(start_x, end_x):
	ready = [True]
	def scan_action(x, y):
		e_type = get_entity_type()
		if e_type == Entities.Dead_Pumpkin:
			prepare_soil()
			plant(Entities.Pumpkin)
			ready[0] = False
		else:
			if e_type != Entities.Pumpkin:
				prepare_soil()
				plant(Entities.Pumpkin)
				ready[0] = False
			else:
				if not can_harvest():
					ready[0] = False
	traverse_columns(start_x, end_x, scan_action)
	move_to_x(0)
	move_to_y(0)
	return ready[0]

def farm_pumpkin():
	count = get_worker_count()
	ranges = split_columns(count)
	for i in range(1, len(ranges)):
		r = ranges[i]
		spawn_drone(pumpkin_zone, r[0], r[1])
	r0 = ranges[0]
	p_start, p_end = r0[0], r0[1]
	def initial_pumpkin(x, y):
		prepare_soil()
		plant(Entities.Pumpkin)
	traverse_columns(p_start, p_end, initial_pumpkin)
	while True:
		if pumpkin_primary_scan(p_start, p_end):
			pass_count = 0
			while pass_count < PUMPKIN_PASSES:
				pumpkin_primary_scan(p_start, p_end)
				pass_count += 1
			harvest()
			traverse_columns(p_start, p_end, initial_pumpkin)

def start_weird_substance():
	count = get_worker_count()
	ranges = split_columns(count)
	for i in range(1, len(ranges)):
		r = ranges[i]
		def weird_drone(s, e):
			def weird_action(x, y):
				prepare_soil()
				plant(Entities.Carrot)
				use_item(Items.Fertilizer)
			traverse_columns(s, e, weird_action)
		spawn_drone(weird_drone, r[0], r[1])
	r0 = ranges[0]
	farm_normal_zone(r0[0], r0[1], Entities.Carrot, True)

def solve_maze():
	directions = [North, East, South, West]
	facing = 0
	while get_entity_type() != Entities.Treasure:
		right = (facing + 1) % 4
		if can_move(directions[right]):
			facing = right
			move(directions[facing])
			continue
		if can_move(directions[facing]):
			move(directions[facing])
			continue
		left = (facing - 1) % 4
		if can_move(directions[left]):
			facing = left
			move(directions[facing])
			continue
		facing = (facing + 2) % 4
		move(directions[facing])
	harvest()

def farm_maze():
	while True:
		clear()
		move_to_column_bottom(0)
		if get_entity_type() != Entities.Bush:
			plant(Entities.Bush)
		maze_size = get_world_size() * 2**(num_unlocked(Unlocks.Mazes) - 1)
		if num_items(Items.Weird_Substance) >= maze_size:
			use_item(Items.Weird_Substance, maze_size)
			solve_maze()

def collect(size=get_world_size(), max_length=None):
	shortcut_limit = size ** 2 // 3
	clear()
	set_world_size(size)
	change_hat(Hats.Dinosaur_Hat)
	while not patrol_grid(shortcut_limit, max_length):
		change_hat(Hats.Straw_Hat)
		change_hat(Hats.Dinosaur_Hat)
	change_hat(Hats.Straw_Hat)

def patrol_grid(shortcut, max_length):
	size = get_world_size()
	target = measure()
	length = 0
	while target:
		pos = get_pos_x(), get_pos_y()
		x, y = pos
		directions = get_directions(pos, size)
		x_dir, y_dir = directions
		if pos == target:
			target = measure()
			length += 1
		if max_length != None:
			if length >= max_length:
				return True
		if length >= (size ** 2 - 1) * 0.98:
			if not can_move(x_dir) and not can_move(y_dir):
				return True
		if length <= size // 2:
			t_x, t_y = target
			move_pos(t_x, get_pos_y())
			move_pos(get_pos_x(), t_y)
			if (get_pos_x(), get_pos_y()) == (x, y):
				for d in [North, South, East, West]:
					if move(d):
						break
			else:
				continue
		target, length = move_to_target(
			pos, target, size, length, directions, shortcut
		)
		if (get_pos_x(), get_pos_y()) == (x, y):
			if length >= (size ** 2 - 1):
				return True
			else:
				quick_print("Failed at length:", length)
				return False

def get_directions(pos, size):
	x, y = pos
	if y >= size // 2:
		x_dir = East
	else:
		x_dir = West
	if x % 2 == 0:
		y_dir = North
	else:
		y_dir = South
	return x_dir, y_dir

def get_boundaries(pos, target, size, directions):
	x, y = pos
	t_x, t_y = target
	x_dir, y_dir = directions
	same_half = (y < size // 2) == (t_y < size // 2)
	if x_dir == East:
		ahead = x < t_x and same_half
		behind = x > t_x and same_half
		x_bound = size - 1
		y_min = size // 2
		y_max = size - 1
		y_bounds = y_min, y_max
		y_next = y_min - 1
	else:
		ahead = x > t_x and same_half
		behind = x < t_x and same_half
		x_bound = 0
		y_min = 0
		y_max = size // 2 - 1
		y_bounds = y_min, y_max
		y_next = y_max + 1
	return ahead, behind, x_bound, y_bounds, y_next

def move_to_target(pos, target, size, length, directions, shortcut):
	x, y = pos
	t_x, t_y = target
	x_dir, y_dir = directions
	ahead, behind, x_bound, y_bounds, y_next = get_boundaries(
		pos, target, size, directions
	)
	y_min, y_max = y_bounds
	if measure():
		if at_y_bound(y_dir, y_min, y_max):
			if at_half_grid_end(x_bound, y_bounds):
				move(y_dir)
			else:
				move(x_dir)
		elif not move(y_dir):
			if not move(x_dir):
				length = size ** 2 - 1
	elif length <= shortcut and can_move(x_dir):
		if not ahead and not behind:
			body_columns = length // (size // 2) - 2
			if length <= shortcut // 2:
				body_columns -= 2
			for _ in range(max(0, body_columns)):
				move_serpentine(
					target, directions, x_bound, y_bounds
				)
				pos = get_pos_x(), get_pos_y()
				if pos == target:
					return target, length
				directions = get_directions(pos, size)
				ahead, _, x_bound, y_bounds, _ = get_boundaries(
					pos, target, size, directions
				)
				if ahead:
					break
		x, y = get_pos_x(), get_pos_y()
		if ahead:
			x_dir, y_dir = directions
			y_min, y_max = y_bounds
			if not y_ahead(target, y_dir):
				if y_dir == North:
					y_bound = y_max
				else:
					y_bound = y_min
				move_shortcut(target, x, y_bound, x_bound, y_bounds)
				move(x_dir)
				x = get_pos_x()
			move_shortcut(target, x, t_y, x_bound, y_bounds)
			move_shortcut(target, t_x, t_y, x_bound, y_bounds)
		else:
			move_shortcut(target, x_bound, y, x_bound, y_bounds)
			move_shortcut(target, x_bound, y_next, x_bound, y_bounds)
	else:
		move_serpentine(target, directions, x_bound, y_bounds)
	return target, length

def move_shortcut(target, x, y, x_bound, y_bounds):
	size = get_world_size()
	pos = get_pos_x(), get_pos_y()
	pos_x, pos_y = pos
	directions = get_directions(pos, size)
	x_dir, y_dir = directions
	t_x, t_y = target
	y_min, y_max = y_bounds
	for _ in range(abs(pos_x - x)):
		if get_pos_x() == t_x and get_pos_y() == t_y:
			return
		if not move(x_dir):
			return
	pos = get_pos_x(), get_pos_y()
	pos_x, pos_y = pos
	x_dir, y_dir = get_directions(pos, size)
	for _ in range(abs(pos_y - y)):
		if at_y_bound(y_dir, y_min, y_max):
			if at_half_grid_end(x_bound, y_bounds):
				move(y_dir)
				if t_x == size - 1 or t_x == 0:
					pos = get_pos_x(), get_pos_y()
					directions = get_directions(pos, size)
					_, _, x_bound, y_bounds, _ = get_boundaries(
						pos, target, size, directions
					)
					move_serpentine(
						target, directions, x_bound, y_bounds
					)
			else:
				move(x_dir)
			return
		if get_pos_x() == t_x and get_pos_y() == t_y:
			return
		if not move(y_dir):
			return

def move_serpentine(target, directions, x_bound, y_bounds):
	x_dir, y_dir = directions
	y_min, y_max = y_bounds
	t_x, t_y = target
	size = get_world_size()
	x = get_pos_x()
	same_half_column = (x == t_x and y_min <= t_y <= y_max)
	if not same_half_column:
		if y_dir == North:
			y_bound = y_max
		else:
			y_bound = y_min
		for _ in range(abs(y_bound - get_pos_y())):
			move(y_dir)
	while not measure():
		if at_half_grid_end(x_bound, y_bounds):
			move(y_dir)
			return
		if at_y_bound(y_dir, y_min, y_max):
			while not move(x_dir):
				back = reverse_direction(y_dir)
				if not move(back):
					break
			return
		while not move(y_dir):
			back = reverse_direction(x_dir)
			if not move(back):
				move(x_dir)
				x, y = get_pos_x(), get_pos_y()
				x_dir, y_dir = get_directions((x, y), size)
				if y >= size // 2:
					for _ in range(abs(y - size)):
						if not move(y_dir):
							return
				else:
					if y == 0 and not move(y_dir):
						return
					for _ in range(y):
						if not move(y_dir):
							return

def at_half_grid_end(x_bound, y_bounds):
	y_min, y_max = y_bounds
	x, y = get_pos_x(), get_pos_y()
	if x_bound == 0:
		grid_end = x == x_bound and y == y_max
	else:
		grid_end = x == x_bound and y == y_min
	return grid_end

def at_y_bound(y_dir, y_min, y_max):
	y = get_pos_y()
	if y_dir == North:
		return y == y_max
	else:
		return y == y_min

def y_ahead(target, direction):
	x, y = target
	if direction == North:
		if y >= get_pos_y():
			return True
	elif direction == South:
		if y <= get_pos_y():
			return True
	return False

def reverse_direction(direction):
	if direction == North:
		reverse = South
	elif direction == South:
		reverse = North
	elif direction == East:
		reverse = West
	elif direction == West:
		reverse = East
	else:
		reverse = None
	return reverse

def move_pos(x, y):
	while x != get_pos_x():
		if x > get_pos_x():
			if not move(East):
				return False
		if x < get_pos_x():
			if not move(West):
				return False
	while y != get_pos_y():
		if y > get_pos_y():
			if not move(North):
				return False
		if y < get_pos_y():
			if not move(South):
				return False
	return True

def run_farm():
	if MODE == "normal":
		if FERTILIZE:
			start_weird_substance()
		else:
			start_normal()
	elif MODE == "wood":
		start_wood()
	elif MODE == "mixed":
		start_mixed()
	elif MODE == "pumpkin":
		farm_pumpkin()
	elif MODE == "cactus":
		start_cactus()
	elif MODE == "dinosaur":
		while True:
			max_len = None
			if TARGET_COST != None:
				bones_needed = TARGET_COST - num_items(Items.Bone)
				max_length = get_world_size() ** 2
				boost = 2 ** (num_unlocked(Unlocks.Dinosaurs) - 1)
				for idx in range(max_length + 1):
					if idx ** 2 * boost >= bones_needed:
						max_length = idx
						break
				max_len = max_length
			collect(get_world_size(), max_len)
	elif MODE == "maze":
		farm_maze()

clear()
run_farm()
