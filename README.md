# Pydip


Pydip is a python program with the main objective to give a stereoplot reading practice platform by generating random planes, folds, faults and focal mechanisms.
As a secondary future objective, for now not implemented, the software will be able to plot and elaborate structural measurements obtained on the field (similar to [Stereonet](https://www.rickallmendinger.net/stereonet)).

## Capabilities:

The capabilities of the software are:

+ Generate multiple random sets of planes
+ Generate multiple random sets of folds
+ Generate random focal mechanisms
+ Data table view and selection
+ Import and plot imported data

### Generate random planes

![](/images/1.png)

![](/images/4.png)

Pydip is able to generate n sets of random planes composed by a set number of planes. The program chooses a random dip direction and angle for every set and depending on that plane the planes will be generated with a normal distribuition with a random std value.

The parameters that can be tweaked are:

+ Number of sets
+ Number of planes
+ Plot planes and/or poles

### Generate random folds

![](/images/2.png)

Pydip is able to generate n sets of random planes that follow random cilindrical fold parameters (axial plane and hinge line inclination etcetc). 

The parameters that can be tweaked are:

+ Number of sets of folds
+ Number of planes for every fold limb
+ Plot limb planes and/or poles 
+ Plot plane axis and/or hinge line

### Generate focal mechanisms

![](/images/3.png)


## Planned features:

+ Faults
+ Better selection options
+ Better import functions
+ Statistics module
+ 3D viewer for plotted structures
