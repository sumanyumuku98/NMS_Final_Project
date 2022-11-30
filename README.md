# DCASim 
A discrete event simulator for distributed consensus algorithms [[Wiki]](https://github.com/RukNdf/DCASim/wiki)

DCASim allows for the simulation of higly abstracted implementations of distributed consensus algorithms. It was made as a tool to help understand and test the workings of higly distributed consensus algorithms without the need for a complex implementation. 

As the abstract implementations lack the optimization a real implementation would have the simulation can't properly account for processing time and is therefore unsuitable for the avaliation of real world performance. The only delay in the systems are point to point latency which limits the usage in systems with other more significant factors (e.g. consensus in clusters, blockchain, and consensus with limited throughput) to verifying the correctness of the algoritms. 




## Files
#### base.py
Base simulation file. Contains all necessary structures and functions required for the simulation. 
#### svg.py
svg generator. Makes an svg image from the simulation log. 
#### simple/
Simple example. Shows the implementation of the simplest possible consensus algorithm. 
#### pseudo-paxos/
Another example. Shows the implementation of a paxos-like algorithm.
#### multipaxos/
Multipaxos algorithm.

## Basic Usage
All main files require both the base.py and the svg.py files to work. As the paths are relative they must be executed from within their folders. 

e.g.
```simple> python sim.py```

Currently all main files are set to simulate their working based on local example files, print messages to the terminal, and output the working as a svg file.

![](https://raw.githubusercontent.com/RukNdf/DCASim/main/multi.svg)

For more information read the [wiki](https://github.com/RukNdf/DCASim/wiki).
