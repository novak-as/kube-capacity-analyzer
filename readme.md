 This is quick and dirty **MVP** which

- loads available EC2 instances
- loads description of all pods in k8s cluster 
- calculates **cheapest** possible placement

# Model

Given set of $T$ available hosts with known $AvailableRam_t$, and $AvailableCpu_t$, and set of $P$ pods with known
$RequirementRam_p$ and $RequirementCpu_p$ in worst-case scenario (1 pod goes to separate instance) we will have to use
$I_t = P, \forall t \in \set {0 \dotsc T}$ instances.
Saying that if instance number $i$ of type $t$ is in use described by $InUse_i^t$ then our total price will be
$$\sum_{t=0}^{T} \sum_{i=0}^{I_t} \left( Price_t * InUse_i^t \right)$$

We also should consider such limitations as:

- we can not overexceed instance capacity by ram or cpu, in other words:
$$\sum_{p=0}^{P} \left( RequirementRam_p * M_p^{i_t} \right) \le AvailableRam_t, \forall i \in \set{0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

$$\sum_{p=0}^{P} \left( RequirementCpu_p * M_p^{i_t} \right) \le AvailableCpu_t, \forall i \in \set{0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

- every pod should be placed, and every pod should be placed exactly 1 time:
$$\sum_{i=0}^{I_t} M_p^{i_t} = 1, \forall p \in \set{0 \dotsc P}, \forall t \in \set {0 \dotsc T}$$

We should also specify that instance $i$ of type $t$ is in use only if at least one pod is placed there,
i.e $InUse_i^t = 1$ if $\sum\nolimits_{p=0}^P M_p^{i_t} > 0$ else $0$.
Since this is not a valid description in terms of linear programming this can be replaced with the set of equations
$$InUse_i^t \ge { \sum_\nolimits{p=0}^P M_p^{i_t}  \over P }, \forall i \in \set{0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

$$InUse_i^t \le P-1 + { \sum\nolimits_{p=0}^P M_p^{i_t}  \over P }, \forall i \in \set{0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

Not mandatory for calculation correctness, but is a good relaxation to reduce search area to limit that instances 
should be used sequentially (i.e there is no sense to calculate placement for instance $5$ if instance $4$ is still not in use). 
To achieve this we can specify another constraint:
$$InUse_{i-1}^t \ge InUse_i^t, \forall i \in \set{1 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$


To summarize, our formulation be

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

$$M_p^{i_t} \in \set \{0 \dotsc 1\}, \forall i \in \set {0 \dotsc I_t\}, \forall p \in \set{0 \dotsc P}, \forall t \in \set {0 \dotsc T}$$

$$InUse_i^t  \in \set \{0 \dotsc 1\}, \forall i \in \set {0 \dotsc I_t}, \forall t \in \set {0 \dotsc T}$$

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
