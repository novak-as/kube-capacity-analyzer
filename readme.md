 This is quick and dirty **MVP** which

- loads available EC2 instances
- loads description of all pods in k8s cluster 
- calculates **cheapest** possible placement

# Model

Minimize:

$$
\sum_{t=0}^{T} \sum_{i=0}^{I_t} \left( Price_t * InUse_i^t \right)
$$


Subject to:

$$\sum_{p=0}^{P} \left( RequirementRam_p * M_p^{i_t} \right) \le AvailableRam_t, \forall i \in \set{0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

$$\sum_{p=0}^{P} \left( RequirementCpu_p * M_p^{i_t} \right) \le AvailableCpu_t, \forall i \in \set{0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

$$\sum_{i=0}^{I_t} M_p^{i_t} = 1, \forall p \in \set{0 \dotsc P}, \forall t \in \set {0 \dotsc T}$$

$$InUse_i^t \ge { \sum_\nolimits{p=0}^P M_p^{i_t}  \over P }, \forall i \in \set{0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

$$InUse_i^t \le P-1 + { \sum\nolimits_{p=0}^P M_p^{i_t}  \over P }, \forall i \in \set{0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

$$InUse_{i-1}^t \ge InUse_i^t, \forall i \in \set{1 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

$$M_p^{i_t} \in \{0 \dotsc 1\}, \forall i \in \{0 \dotsc I_t\}, \forall p \in \set{0 \dotsc P}, \forall t \in \set {0 \dotsc T}$$

$$InUse_i^t  \in \{0 \dotsc 1\}, \forall i \in \set{0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

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