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
    def __init__(self,seq,opfs,opfd,ipfs,ipfd,cs,cd,dfs,dfd,runs):
        self.seq = seq
        self.opfs = opfs
        self.opfd = opfd
        self.ipfs = ipfs
        self.ipfd = ipfd
        self.cs = cs
        self.cd = cd
        self.dfs = dfs
        self.dfd = dfd
        self.runs: list[Run] = runs
    def fill_lists(self):
        for run in self.runs:
            if run.loop == "Sequential":
                self.seq.append(run)
            if run.loop == "Single Outer Parallel For" and run.scheduling == "static":
                self.opfs.append(run)
            if run.loop == "Single Outer Parallel For" and run.scheduling == "dynamic":
                self.opfd.append(run)
            if run.loop == "Single Inner Parallel For" and run.scheduling == "static":
                self.ipfs.append(run)
            if run.loop == "Single Inner Parallel For" and run.scheduling == "dynamic":
                self.ipfd.append(run)
            if run.loop == "Collapse(2)" and run.scheduling == "static":
                self.cs.append(run)
            if run.loop == "Collapse(2)" and run.scheduling == "dynamic":
                self.cd.append(run)
            if run.loop == "Double For" and run.scheduling == "static":
                self.dfs.append(run)
            if run.loop == "Double For" and run.scheduling == "dynamic":
                self.dfd.append(run)
            
    def average_out(self):
        lists = {
            "Sequential": self.seq,
            "Outer Parallel For Static": self.opfs,
            "Outer Parallel For Dynamic": self.opfd,
            "Inner Parallel For Static": self.ipfs,
            "Inner Parallel For Dynamic": self.ipfd,
            "Collapse Static": self.cs,
            "Collapse Dynamic": self.cd,
            "Double Static": self.dfs,
            "Double Dynamic": self.dfd
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
        print(f"{self.seq[0]}\n{self.opfs[0]}\n{self.opfd[0]}\n{self.ipfs[0]}\n{self.ipfd[0]}\n{self.cs[0]}\n" + 
              f"{self.cd[0]}\n{self.dfs[0]}\n{self.dfd[0]}\n")
    def plot_against_sequential(self, averages, metric, ylabel):
        baseline_data = averages["Sequential"]
        baseline_thread = sorted(baseline_data.keys())[0]
        baseline = baseline_data[baseline_thread][metric]

        plt.figure(figsize=(12, 7))

        for name, thread_data in averages.items():
            if name == "Sequential":
                continue

            threads = sorted(thread_data.keys())
            times = [thread_data[t][metric] for t in threads]

            plt.plot(
                threads,
                times,
                marker="o",
                label=name
            )

        plt.axhline(
            y=baseline,
            linestyle="--",
            label=f"Sequential baseline ({baseline:.3f}s)"
        )

        plt.xlabel("Number of threads")
        plt.ylabel(ylabel)
        plt.title(f"Parallel Configurations vs Sequential Baseline: {ylabel}")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"all_vs_sequential_{metric}.png", dpi=300)
        plt.close()
    def plot_comparison(self,averages,metric,ylabel,name_1,name_2):
        x = averages[name_1]
        y = averages[name_2]

        x_threads = sorted(x.keys())
        y_threads = sorted(y.keys())

        x_times = [x[t][metric] for t in x_threads]
        y_times = [y[t][metric] for t in y_threads]

        plt.figure(figsize = (10,6))
        plt.plot(
            x_threads,
            x_times,
            marker="o",
            label=name_1
        )
        plt.plot(
            y_threads,
            y_times,
            marker="o",
            label=name_2
        )
        plt.xlabel("Number of threads")
        plt.ylabel(ylabel)
        plt.title(f"{name_1} vs {name_2}: {ylabel}")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{name_1}_vs_{name_2}_{metric}.png", dpi=300)
        plt.close()

src = sys.argv[1] if len(sys.argv) > 1 else "method-a-results.csv"
runs = []

with open(src) as f:
    reader = csv.DictReader(f)
    for line in reader:
        run = Run(str(line["method"]),str(line["size"]),str(line["loop_type"]),str(line["schedule"]),
        int(line["run"]),int(line["threads"]),float(line["wall"]),float(line["user"]),float(line["sys"]))
        runs.append(run)

sequential = []
outer_parallel_for_static= []
outer_parallel_for_dynamic = []
inner_parallel_for_static = []
inner_parallel_for_dynamic = []
collapse_static = []
collapse_dynamic = []
double_for_static = []
double_for_dynamic = []

az = Analyser(sequential,outer_parallel_for_static,outer_parallel_for_dynamic,inner_parallel_for_static,
              inner_parallel_for_dynamic,collapse_static,collapse_dynamic,double_for_static,double_for_dynamic,runs)
az.fill_lists()
#az.print_list_heads()

averages = az.average_out()

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Sequential","Outer Parallel For Static")
az.plot_comparison(averages, "speedup", "Speedup","Sequential","Outer Parallel For Static")
az.plot_comparison(averages, "efficiency", "Efficiency","Sequential","Outer Parallel For Static")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Sequential","Inner Parallel For Static")
az.plot_comparison(averages, "speedup", "Speedup","Sequential","Inner Parallel For Static")
az.plot_comparison(averages, "efficiency", "Efficiency","Sequential","Inner Parallel For Static")


az.plot_comparison(averages, "wall", "Wall Time (seconds)","Inner Parallel For Static","Outer Parallel For Static")
az.plot_comparison(averages, "user", "CPU Time (seconds)","Inner Parallel For Static","Outer Parallel For Static")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Inner Parallel For Dynamic","Outer Parallel For Dynamic")
az.plot_comparison(averages, "user", "CPU Time (seconds)","Inner Parallel For Dynamic","Outer Parallel For Dynamic")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Outer Parallel For Static","Outer Parallel For Dynamic")
az.plot_comparison(averages, "wall", "Wall Time (seconds)","Inner Parallel For Static","Inner Parallel For Dynamic")
#Frontrunner: inner parallel for dynamic
az.plot_against_sequential(averages, "wall", "Wall Time (seconds)")
az.plot_against_sequential(averages, "user", "User CPU Time (seconds)")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Collapse Static","Collapse Dynamic")
az.plot_comparison(averages, "wall", "Wall Time (seconds)","Collapse Dynamic","Inner Parallel For Dynamic")

az.plot_comparison(averages, "wall", "Wall Time (seconds)","Double Static","Double Dynamic")
az.plot_comparison(averages, "wall", "Wall Time (seconds)","Collapse Dynamic","Double Dynamic")

#33 entries total
az.plot_comparison(averages, "speedup", "Speedup","Inner Parallel For Static","Outer Parallel For Static")
#Inner Parallel For Static
az.plot_comparison(averages, "speedup", "Speedup","Inner Parallel For Dynamic","Outer Parallel For Dynamic")
#Inner Parallel For Dynamic
az.plot_comparison(averages, "speedup", "Speedup","Inner Parallel For Static","Inner Parallel For Dynamic")
#Inner Parallel For Dynamic
az.plot_comparison(averages, "speedup", "Speedup","Collapse Static","Collapse Dynamic")
#Unclear: Static 16, Dynamic 17
az.plot_comparison(averages, "speedup", "Speedup","Double Static","Double Dynamic")
#Double Dynamic(only just)
az.plot_comparison(averages, "speedup", "Speedup","Collapse Static","Double Dynamic")
#Collapse Static
az.plot_comparison(averages, "speedup", "Speedup","Double Static","Collapse Dynamic")


az.plot_comparison(averages, "efficiency", "Efficiency","Inner Parallel For Static","Outer Parallel For Static")
#Inner Parallel For Static
az.plot_comparison(averages, "efficiency", "Efficiency","Inner Parallel For Dynamic","Outer Parallel For Dynamic")
#Inner Parallel For Dynamic
az.plot_comparison(averages, "efficiency", "Efficiency","Inner Parallel For Static","Inner Parallel For Dynamic")
#Inner Parallel For Dynamic
az.plot_comparison(averages, "efficiency", "Efficiency","Collapse Static","Collapse Dynamic")
#Unclear: Static 16, Dynamic 17
az.plot_comparison(averages, "efficiency", "Efficiency","Double Static","Double Dynamic")
#Double Dynamic(only just)
az.plot_comparison(averages, "efficiency", "Efficiency","Collapse Static","Double Dynamic")
#Collapse Static
az.plot_comparison(averages, "efficiency", "Efficiency","Double Static","Collapse Dynamic")
#Collapse Dynamic

az.plot_comparison(averages, "wall", "Wall","Inner Parallel For Dynamic","Double Static")
az.plot_comparison(averages, "speedup", "Speedup","Inner Parallel For Dynamic","Double Static")
az.plot_comparison(averages, "efficiency", "Efficiency","Inner Parallel For Dynamic","Double Static")
az.plot_comparison(averages, "wall", "Wall","Inner Parallel For Dynamic","Double Dynamic")
az.plot_comparison(averages, "speedup", "Speedup","Inner Parallel For Dynamic","Double Dynamic")
az.plot_comparison(averages, "efficiency", "Efficiency","Inner Parallel For Dynamic","Double Dynamic")

az.plot_comparison(averages, "wall", "Wall","Collapse Dynamic","Inner Parallel For Dynamic")
az.plot_comparison(averages, "speedup", "Speedup","Collapse Dynamic","Inner Parallel For Dynamic")
az.plot_comparison(averages, "efficiency", "Efficiency","Collapse Dynamic","Inner Parallel For Dynamic")

az.plot_comparison(averages, "wall", "Wall","Collapse Dynamic","Double Dynamic")
az.plot_comparison(averages, "speedup", "Speedup","Collapse Dynamic","Double Dynamic")
az.plot_comparison(averages, "efficiency", "Efficiency","Collapse Dynamic","Double Dynamic")