This is quick and dirty **MVP** which

- loads available EC2 instances
- loads description of all pods in k8s cluster 
- calculates **cheapest** possible placement


Output example:
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