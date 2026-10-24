import subprocess, sys
subprocess.run([sys.executable, "Maintainers/MaintainBills.py"])
subprocess.run([sys.executable, "Maintainers/MaintainQuestions.py"])
subprocess.run([sys.executable, "Maintainers/MaintainVotes.py"])
subprocess.run([sys.executable, "Maintainers/MaintainDebates.py"])

subprocess.run([sys.executable, "Maintainers/MaintainMembers.py"])

subprocess.run([sys.executable, "Maintainers/MaintainStats.py"])
subprocess.run([sys.executable, "Maintainers/MaintainComposition.py"])
