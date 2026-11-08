import csv
import sys
import matplotlib.pyplot as plt
from statistics import mean
class Run:
    def __init__(self,method,size,loop,scheduling,run,threads,wall,user,sys):
        self.method: str = method
        self.size: str = size
        self.loop: str = loop
        self.scheduling: str = scheduling
        self.run: int = run
        self.threads: int = threads
        self.wall: float = wall
        self.user:float = user
        self.sys: float = sys
    def __str__(self):
        return (
            f"Method: {self.method}, Size: {self.size}, "
            f"Loop: {self.loop}, Scheduling: {self.scheduling or 'N/A'}, "
            f"Run: {self.run}, Threads: {self.threads}, "
            f"Wall: {self.wall:.3f}s, User: {self.user:.3f}s, "
            f"System: {self.sys:.3f}s"
        )

class Analyser:
    def __init__(self,seq,bps,bpd,chunk_s,chunk_d,chunk_c,chunk_a,runs):
        self.seq = seq
        self.bps = bps
        self.bpd = bpd
        self.chunk_s = chunk_s
        self.chunk_d = chunk_d
        self.chunk_c = chunk_c
        self.chunk_a = chunk_a
        self.runs: list[Run] = runs
    def fill_lists(self):
        for run in self.runs:
            if run.loop == "Sequential":
                self.seq.append(run)
            if run.loop == "Basic Parallelisation" and run.scheduling == "static":
                self.bps.append(run)
            if run.loop == "Basic Parallelisation" and run.scheduling == "dynamic":
                self.bpd.append(run)
            if run.loop == "Split Chunk Overlap Reduction" and run.scheduling == "static":
                self.chunk_s.append(run)
            if run.loop == "Split Chunk Overlap Reduction" and run.scheduling == "dynamic":
                self.chunk_d.append(run)
            if run.loop == "Split Chunk Overlap Reduction" and run.scheduling == "critical":
                self.chunk_c.append(run)
            if run.loop == "Split Chunk Overlap Reduction" and run.scheduling == "atomic":
                self.chunk_a.append(run)
            
    def average_out(self):
        lists = {
            "Sequential": self.seq,
            "Basic Static": self.bps,
            "Basic Dynamic": self.bpd,
            "Chunk Split Static": self.chunk_s,
            "Chunk Split Reduction": self.chunk_s,
            "Chunk Split Dynamic": self.chunk_d,
            "Chunk Split Critical": self.chunk_c,
            "Chunk Split Atomic": self.chunk_a,
            "Empty Placeholder": []
        }

        averages = {}

        for name, run_list in lists.items():
            averages[name] = {}

            for threads in sorted(set(run.threads for run in run_list)):
                thread_runs = [run for run in run_list if run.threads == threads]

                averages[name][threads] = {
                    "wall": mean(run.wall for run in thread_runs),
                    "user": mean(run.user for run in thread_runs),
                    "sys": mean(run.sys for run in thread_runs)
                }
        baseline = averages["Sequential"][1]["wall"]

        for name, thread_data in averages.items():
            baseline = thread_data.get(1)
            for threads, times in thread_data.items():
                times["speedup"] = baseline["wall"] / times["wall"]
                times["efficiency"] = times["speedup"] / threads
        return averages
    def print_list_heads(self):
        print(f"{self.seq[0]}\n{self.bps[0]}\n{self.bpd[0]}\n")
    def plot_comparison(self,averages,metric,ylabel,name_1,name_2,name_3=None):
        x = averages[name_1]
        y = averages[name_2]

        x_threads = sorted(x.keys())
        y_threads = sorted(y.keys())

        x_times = [x[t][metric] for t in x_threads]
        y_times = [y[t][metric] for t in y_threads]

        plt.figure(figsize = (10,6))
        plt.plot(x_threads,x_times,marker="o",label=name_1)
        plt.plot(y_threads,y_times,marker="o",label=name_2)
        if name_3:
            z = averages[name_3]
            z_threads = sorted(z.keys())
            z_times = [z[t][metric] for t in z_threads]
            plt.plot(z_threads,z_times,marker="o",label=name_3)
            plt.xlabel("Number of threads")
            plt.ylabel(ylabel)
            plt.title(f"{name_1} vs {name_2} vs {name_3}: {ylabel}")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{name_1}_vs_{name_2}_vs_{name_3}_{metric}.png", dpi=300)
            plt.close()
        else:
            plt.xlabel("Number of threads")
            plt.ylabel(ylabel)
            plt.title(f"{name_1} vs {name_2}: {ylabel}")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{name_1}_vs_{name_2}_{metric}.png", dpi=300)
            plt.close()

src = sys.argv[1] if len(sys.argv) > 1 else "method-b-results.csv"
runs = []

with open(src) as f:
    reader = csv.DictReader(f)
    for line in reader:
        run = Run(str(line["method"]),str(line["size"]),str(line["loop_type"]),str(line["schedule"]),
        int(line["run"]),int(line["threads"]),float(line["wall"]),float(line["user"]),float(line["sys"]))
        runs.append(run)

az = Analyser([],[],[],[],[],[],[],runs)
az.fill_lists()

averages = az.average_out()

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Basic Static","Sequential")
az.plot_comparison(averages, "speedup", "Speedup","Basic Static","Sequential")
az.plot_comparison(averages, "efficiency", "Efficiency","Basic Static","Sequential")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Basic Static","Basic Dynamic")
az.plot_comparison(averages, "speedup", "Speedup","Basic Static","Basic Dynamic")
az.plot_comparison(averages, "efficiency", "Efficiency","Basic Static","Basic Dynamic")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Chunk Split Static","Basic Static")
az.plot_comparison(averages, "speedup", "Speedup","Chunk Split Static","Basic Static")
az.plot_comparison(averages, "efficiency", "Efficiency","Chunk Split Static","Basic Static")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Chunk Split Static","Chunk Split Dynamic")
az.plot_comparison(averages, "speedup", "Speedup","Chunk Split Static","Chunk Split Dynamic")
az.plot_comparison(averages, "efficiency", "Efficiency","Chunk Split Static","Chunk Split Dynamic")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Chunk Split Reduction","Chunk Split Critical")
az.plot_comparison(averages, "speedup", "Speedup","Chunk Split Reduction","Chunk Split Critical")
az.plot_comparison(averages, "efficiency", "Efficiency","Chunk Split Reduction","Chunk Split Critical")
az.plot_comparison(averages, "user", "CPU Time","Chunk Split Reduction","Chunk Split Critical")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Chunk Split Reduction","Chunk Split Critical","Chunk Split Atomic")
az.plot_comparison(averages, "speedup", "Speedup","Chunk Split Reduction","Chunk Split Critical","Chunk Split Atomic")
az.plot_comparison(averages, "efficiency", "Efficiency","Chunk Split Reduction","Chunk Split Critical","Chunk Split Atomic")
az.plot_comparison(averages, "user", "CPU Time","Chunk Split Reduction","Chunk Split Critical","Chunk Split Atomic")