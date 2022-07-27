This is quick and dirty **MVP** which

- loads available EC2 instances
- loads description of all pods in k8s cluster 
- calculates **cheapest** possible placement

# Model

Minimize:

$$
\sum_{i=0}^{I} \left( Price_i * InUse_i \right)
$$


Subject to:

$$\sum_{p=0}^{P} \left( RequirementRam_p * M_p^i \right) \le AvailableRam_i, \forall i \in \set{0 \dotsc I}$$

$$\sum_{p=0}^{P} \left( RequirementCpu_p * M_p^i \right) \le AvailableCpu_i, \forall i \in \set{0 \dotsc I}$$

$$\sum_{i=0}^{I} M_p^i = 1, \forall p \in \set{0 \dotsc P}$$

$$InUse_i \ge { \sum_\nolimits{p=0}^P M_p^i  \over P }, \forall i \in \set{0 \dotsc I}$$

$$InUse_i \le P-1 + { \sum\nolimits_{p=0}^P M_p^i  \over P }, \forall i \in \set{0 \dotsc I}$$

$$InUse_{i-1} \ge InUse_i, \forall i \in \set{1 \dotsc I}$$

$$M_p^i \in \{0 \dotsc 1\}, \forall i \in \{0 \dotsc I\}, \forall p \in \set{0 \dotsc P}$$

$$InUse_i  \in \{0 \dotsc 1\}, \forall i \in \set{0 \dotsc I}$$

# Result
```
AwsInstanceType(name='r6g.medium', ram=8192, cpu=1, price=0.0504) N 4 Total booked capacity 5200.0 ram, 0.9 cpu:
- Pod number 3 DeploymentRequirement(ram=700, cpu=0.2)
- Pod number 4 DeploymentRequirement(ram=500, cpu=0.2)
- Pod number 5 DeploymentRequirement(ram=4000, cpu=0.5)

AwsInstanceType(name='t2.micro', ram=1024, cpu=1, price=0.0162) N 4 Total booked capacity 700.0 ram, 0.5 cpu:
- Pod number 0 DeploymentRequirement(ram=100, cpu=0.1)
- Pod number 1 DeploymentRequirement(ram=100, cpu=0.2)
- Pod number 2 DeploymentRequirement(ram=500, cpu=0.2)
```