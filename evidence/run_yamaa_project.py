import sys, time
import yamaa
t=time.time()
proj = yamaa.project(sys.argv[1])
runs = proj.run("adam")
print(runs)
runs.save()
print("seconds", round(time.time()-t,1))
