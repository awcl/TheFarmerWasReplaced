# The Farmer Was Replaced - Automated Farming Script

An advanced Python-based automation and drone-management script for *The Farmer Was Replaced*, utilizing algorithmic grid traversal, parallel multi-drone load balancing, and heuristic-based puzzle solving.

## Algorithmic & Architectural Overview

- **Dynamic Resource Configuration & State Mapping:** Features a centralized configuration table (`RESOURCE_CONFIG`) mapping target IDs to crop parameters, soil requirements, worker allocations, and fertilizer flags, driving a unified execution dispatcher (`run_farm()`).
- **Parallel Workload Distribution & Column Splitting:** Employs a load-balancing interval splitting algorithm (`split_columns()`) that divides the grid width $N$ across available drone threads (`max_drones()`), ensuring balanced spatial distribution and concurrent execution zones.
- **Snake-Pattern Grid Traversal (`traverse_columns` & `traverse_rows_offset`):** Implements bi-directional alternating serpentine (zigzag) graph traversals over grid coordinates $(x, y)$ to minimize travel distance, optimize entry points based on drone position, and eliminate redundant long-distance movements.
- **Cactus Sorting & Bubble Sort Heuristics (`cactus_swap` & `cactus_is_sorted`):** Utilizes localized and global comparison-based sorting networks. Drones repeatedly measure, compare with orthogonal neighbors (North, South, East, West), and execute conditional swaps (`swap()`) to guarantee complete ascending order before harvesting.
- **Multi-Pass Pumpkin Verification (`pumpkin_primary_scan`):** Implements a multi-pass transactional verification loop (`PUMPKIN_PASSES`). The script scans the field, replaces dead or incorrect entities, and blocks global harvest execution until a complete readiness convergence state (`ready[0] == True`) is achieved.
- **Wall-Following Maze Solver (Left-Hand Rule):** Solves procedurally generated mazes using a relative-direction state machine based on the left-hand rule algorithm. Evaluates directional relative offsets (`can_move`) to navigate labyrinthine structures and locate the treasure entity.
- **Automated Dinosaur Traversal Patterns:** Executes deterministic Hamiltonian-style coordinate tracking matrices and boundary checks while equipped with the Dinosaur Hat, automatically resetting and recovering to origin $(0, 0)$ upon movement obstruction.
