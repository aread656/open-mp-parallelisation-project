import re, csv, sys

src = sys.argv[1] if len(sys.argv) > 1 else "method-a-records.txt"
dst = sys.argv[2] if len(sys.argv) > 2 else "method-a-results.csv"

method = size = loop = schedule = None
run = 0
prev_threads = None
rows = []

line_re = re.compile(
    r"threads:\s*(\d+)\s+wall:\s*([\d.]+)\s+user:\s*([\d.]+)\s+sys:\s*([\d.]+)"
)

with open(src) as f:
    for raw in f:
        line = raw.strip()
        if not line:
            continue

        m = line_re.search(line)
        if m:
            threads, wall, user, sys_t = int(m[1]), float(m[2]), float(m[3]), float(m[4])
            # A drop in thread count means a new repetition started
            if prev_threads is None or threads < prev_threads:
                run += 1
            prev_threads = threads
            rows.append([method, size, loop, schedule, run,
                         threads, wall, user, sys_t])
            continue

        # Header lines
        if line.startswith("Method"):
            parts = line.split()
            method, size = parts[1], parts[2]
        elif line.lstrip("- ").lower() in ("static", "dynamic"):
            schedule = line.lstrip("- ").lower()
            run, prev_threads = 0, None
        else:
            loop = line.lstrip("- ").strip()
            schedule, run, prev_threads = None, 0, None

with open(dst, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["method", "size", "loop_type", "schedule", "run",
                "threads", "wall", "user", "sys"])
    w.writerows(rows)

print(f"Wrote {len(rows)} rows to {dst}")