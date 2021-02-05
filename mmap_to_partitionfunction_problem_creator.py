import argparse
import pyGM
import itertools
from pathlib import Path

FORMULATIONS = [1,2,3]
# F1) simply adds an evidence file for the MAP variables
# F2) adds singleton factors for the MAP variables instantiating them
#     and removes the MAP variables from the scope of any other function
# F3) makes the domain size of the MAP variables zero (effectively removing them)
#     and removes the MAP variables from the scope of any function


parser = argparse.ArgumentParser(description='Partition Function Problem Instance Creator from MMAP Problem Instances')
parser.add_argument('-u','--mmap-uai-file', required=True, help='MMAP UAI instance')
parser.add_argument('-q','--mmap-query-file', required=True, help='MMAP MAX variables')
parser.add_argument('-z','--z-formulation', type=int, required=False, help='Formulation style of the new partition function problem (ex, -z 1, -z 2, -z 3, etc., default = all)')
parser.add_argument('-n','--num-instances', type=int, required=False, help='Max number of new partition function instances to create (max = 100000, default = 100000)')
parser.add_argument('-o','--parent-output-dir', required=False, help='Parent directory under which to create problem folders (default = current folder)')

args = parser.parse_args()

mmap_uai_file = Path(args.mmap_uai_file).absolute()
mmap_query_file = Path(args.mmap_query_file).absolute()
if args.z_formulation:
	zf = args.z_formulation
	assert(zf in FORMULATIONS)
else:
	zf = 0
if args.num_instances:
	n = int(args.num_instances)
	assert(n>0 and n <= 100000)
else:
	n = 100000
if args.parent_output_dir:
	parent_output_dir = Path(args.parent_output_dir).absolute()
	parent_output_dir.mkdir(parents=True, exist_ok=True)
else:
	parent_output_dir = Path().absolute()



def readMAPVars(mmap_query_file):
	buffer = []
	with mmap_query_file.open('r') as fin:
		for line in fin:
			if line.startswith('#'): #skip comment lines
				continue;
			buffer += line.strip().split();
	n_map_vars = int(buffer[0])
	map_vars = [int(x) for x in buffer[1:]]
	assert(len(map_vars)==n_map_vars)
	return map_vars

def getVarDomainSizes(vars, gm):
	domains = []
	for v in vars:
		k = gm.var(v).states
		domains.append(k)
	return domains

def createMAPAssignmentTupleGenerator(map_var_domain_sizes):
	assignmentGenerator = itertools.product( *(list(range(x)) for x in map_var_domain_sizes) )
	return assignmentGenerator



# main part 1

mmap_gm = pyGM.GraphModel(pyGM.readUai(mmap_uai_file))
map_vars = readMAPVars(mmap_query_file)
map_var_domain_sizes = getVarDomainSizes(map_vars, mmap_gm)
map_assignment_generator = createMAPAssignmentTupleGenerator(map_var_domain_sizes)



def newProblemInstancePath(mmap_uai_file, parent_output_dir, i, zf):
	if mmap_uai_file.suffix == '.uai':
		stem = mmap_uai_file.stem.replace("_MMAP", "")
	else:
		stem = mmap_uai_file.name.replace("_MMAP", "")
	z_instance_name = stem + "_" + str(i).zfill(5) + "_F" + str(zf) + "_Z"
	z_problem_filename = z_instance_name + ".uai"
	z_problem_file_path = parent_output_dir / ("Z Formulation " + str(zf)) / z_instance_name / z_problem_filename
	return z_problem_file_path

def createProblemDirectory(z_problem_file_path):
	dir = z_problem_file_path.parent
	dir.mkdir(parents=True, exist_ok=True)

def writeUAI(gm, path):
	pyGM.writeUai(path, gm.factors)

def writeEvidenceFile(z_problem_file_path, map_vars, map_assignment):
	assert(len(map_vars)==len(map_assignment))
	nAssignments = len(map_vars)
	assignment_pairs = zip(map_vars, map_assignment)
	buffer = []
	for v,a in assignment_pairs:
		buffer.append(v)
		buffer.append(a)
	evid_string = " ".join(str(x) for x in buffer)
	z_evid_file_path = z_problem_file_path.with_suffix('.uai.evid')
	with z_evid_file_path.open('w') as fout:
		print(nAssignments, evid_string, file=fout)

def formulation_1(mmap_uai_file, mmap_gm, map_vars, map_assignment, i, parent_output_dir):
	zf = 1
	z_problem_file_path = newProblemInstancePath(mmap_uai_file, parent_output_dir, i, zf)
	createProblemDirectory(z_problem_file_path)
	writeUAI(mmap_gm, z_problem_file_path)
	writeEvidenceFile(z_problem_file_path, map_vars, map_assignment)

def formulation_2(mmap_uai_file, mmap_gm, map_vars, map_assignment, i, parent_output_dir):
	zf = 2
	z_problem_file_path = newProblemInstancePath(mmap_uai_file, parent_output_dir, i, zf)
	createProblemDirectory(z_problem_file_path)
	mmap_gm_to_process = mmap_gm.copy() # deep copy
	mmap_gm_to_process.condition2(map_vars, map_assignment)
	writeUAI(mmap_gm_to_process, z_problem_file_path)

def formulation_3(mmap_uai_file, mmap_gm, map_vars, map_assignment, i, parent_output_dir):
	zf = 3
	z_problem_file_path = newProblemInstancePath(mmap_uai_file, parent_output_dir, i, zf)
	createProblemDirectory(z_problem_file_path)
	mmap_gm_to_process = mmap_gm.copy() # deep copy
	mmap_gm_to_process.condition2(map_vars, map_assignment)
	singleton_assignment_factors = mmap_gm_to_process.factorsWithAny(map_vars)
	assert(len(singleton_assignment_factors)==len(map_vars))
	mmap_gm_to_process.removeFactors(singleton_assignment_factors)
	writeUAI(mmap_gm_to_process, z_problem_file_path)

FORMULATION_CREATORS = {  1 : formulation_1,
						  2 : formulation_2,
						  3 : formulation_3,  }

def createFormulation(zf, mmap_uai_file, mmap_gm, map_vars, map_assignment, i, parent_output_dir):
	try:
		FORMULATION_CREATORS[zf](mmap_uai_file, mmap_gm, map_vars, map_assignment, i, parent_output_dir)
	except:
		raise IndexError('Error: The dict "FORMULATION_CREATORS" was not updated to include this formulation!')

def createAllFormulations(mmap_uai_file, mmap_gm, map_vars, map_assignment, i, parent_output_dir):
	for fxn in FORMULATION_CREATORS.values():
		fxn(mmap_uai_file, mmap_gm, map_vars, map_assignment, i, parent_output_dir)


# main part 2
for i,map_assignment in enumerate(map_assignment_generator):
	if i >= n:
		break;
	if zf:
		createFormulation(zf, mmap_uai_file, mmap_gm, map_vars, map_assignment, i, parent_output_dir)
	else:
		createAllFormulations(mmap_uai_file, mmap_gm, map_vars, map_assignment, i, parent_output_dir)




