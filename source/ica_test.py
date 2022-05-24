# ica_test.py
#
# Performance test of ICA implementation
#

import sys, os, subprocess, time, json

OUTPUTNAME = "ica_test.csv"
VERBOSE = False
DEBUG = False
QUIET = False

def error(msg,code=None):
	if not QUIET:
		print(f"ERROR [{sys.argv[0]}]: {msg}",file=sys.stderr,flush=True)
	if DEBUG:
		raise Exception(f"{msg} (code {code})")
	elif type(code) is int:
		exit(code)

def verbose(msg):
	if VERBOSE:
		print(f"VERBOSE [{sys.argv[0]}]: {msg}",file=sys.stdout,flush=True)

dirs = []
for arg in sys.argv[1:]:

	spec = arg.split("=")
	if not arg.startswith("-"):
		dirs.append(arg)
		continue
	elif len(spec) == 1:
		tag = spec[0]
		value = True
	else:
		tag = spec[0]
		value = spec[1]

	if tag in ["-h","--help","help"]:
		print(f"Syntax: {sys.argv[0]} [-h|--help|help] [-o|--output=CSVNAME] FOLDER ...")
	elif tag in ["-o","--output"]:
		if type(value) is str:
			OUTPUTNAME = value
		else:
			error("output file name is not valid")
	elif tag in ["-v","--verbose"]:
		VERBOSE = True
	elif tag in ["-d","--debug"]:
		DEBUG = True
	elif tag in ["-q","--quiet"]:
		QUIET = True
	else:
		error(f"option '{arg}' is not valid",1)

try:

	OUTPUTCSV = open(OUTPUTNAME,"w")

	if not dirs:
		dirs = [os.getcwd()]

	print("folder,file,node_count,link_count,der_count,baseline_time[s],icatest_time[s]",file=OUTPUTCSV)
	for dir in dirs:
		files = os.listdir(dir)
		for file in sorted(files):
			if file.startswith("R") and file.endswith(".glm"):
				verbose(f"Processing {dir}/{file}...")
				JSONFILE = file.replace('.glm','.json')

				# baseline run
				t0 = time.perf_counter()
				rc = subprocess.run(f"gridlabd {file} -o {JSONFILE}".split(),capture_output=True)
				t0 = time.perf_counter()-t0
				if rc.returncode:
					error(f"{file}: {rc.stderr.decode('utf-8')}",rc.returncode)

				# DER count
				with open(JSONFILE,"r") as fh:
					data = json.load(fh)
					loads = [name for name,props in data["objects"].items() if props["class"] == "load"]
					nodes = [name for name,props in data["objects"].items() if "DER_value" in props.keys()]
					links = [name for name,props in data["objects"].items() if "power_losses" in props.keys()]

				# performance run
				t1 = time.perf_counter()
				rc = subprocess.run(f"gridlabd {file} ica_test.glm".split(),capture_output=True)
				t1 = time.perf_counter()-t1
				if rc.returncode:
					error(f"{file}: {rc.stderr.decode('utf-8')}",rc.returncode)

				print(f"{dir},{file},{len(nodes)},{len(links)},{len(loads)},{round(t0,3)},{round(t1,3)}",file=OUTPUTCSV,flush=True)

except Exception as err:

	if DEBUG:
		raise
	else:
		error(sys.argv[0],err,-1)
