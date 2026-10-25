import subprocess, sys
subprocess.run([sys.executable, "MaintainBills.py"])
subprocess.run([sys.executable, "MaintainQuestions.py"])
subprocess.run([sys.executable, "MaintainVotes.py"])
subprocess.run([sys.executable, "MaintainDebates.py"])

subprocess.run([sys.executable, "MaintainMembers.py"])
subprocess.run([sys.executable, "MaintainParty.py"])

subprocess.run([sys.executable, "MaintainStats.py"])
subprocess.run([sys.executable, "MaintainComposition.py"])

subprocess.run([sys.executable, "MaintainLobbyist.py"])


