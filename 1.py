import subprocess

for i in range(10):
    subprocess.run(["python", "2.py", str(i)])