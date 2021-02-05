# mmap_to_partition_function_instance_creator

 A general Python 3 script to convert MMAP instances to Partition Function problems.
 
The script requires Dr. Alex Ihlers pyGM (https://github.com/ihler/pyGM) which in turn is dependent on python's numpy and sortedcontainers (both of which can be installed using python:  py -m pip install name-of-some-package).

Within the main folder, there is an example folder for which the script has been used to create 100 partition function problems in three different formulations from a single CPD MMAP problem.

Formulation 1: simply adds an evidence file for assignments to the MAP variables of the MMAP problem which.  When the evidence file is read by a solver and the MAP variables are instantiated, the resulting problem is reduced to a summation problem.

Formulation 2: MAP variables still have their original domain size in the uai file, but now we add singleton factors that instantiate the variables (these factors have a value of 1.0 for the domain value to be instantiated, and 0.0 for all other values).  Furthermore, factors that used to contain the MAP variables have been reduced in scope to exclude them based on the instantiation.

Formulation 3: MAP variables now have a domain size of 0.  Factors that used to contain the MAP variables have been reduced in scope to exclude them based on the instantiation.

The newly generated file's filename is: 

the original filename (without .uai or _MMAP if either were present) 
+ 
_[######]_ (a number with leading zeros that indicates how the MAP variables were assigned)
+ 
F[#] (where [#] is the formulation number) 
+ 
_Z (to indicate it is now a partition function problem)