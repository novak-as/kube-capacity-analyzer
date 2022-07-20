from mip import Model, xsum, minimize, BINARY, maximize
from model import DeploymentRequirement, AwsInstanceType
from typing import List

#I'm just lazy to type this everytime
def rlen(something):
    return range(len(something))

class MipModel:

    def __init__(self, available_instances: [AwsInstanceType], requirements: List[DeploymentRequirement]):
        self.available_instances = available_instances
        self.requirements = requirements


    def calculate(self):
        model = Model("model")

        # worst-case scenario - we need 1 separate instance for every pod
        placement_matrix = [[[model.add_var(var_type=BINARY)
                       for pod in rlen(self.requirements)]
                       for instance in rlen(self.requirements)]
                       for type in rlen(self.available_instances)]

        # instance is in use only if at least 1 pod use it as a host
        instances_in_use = [[ xsum(placement_matrix[type][instance]) for instance in rlen(self.requirements) ]
                            for type in rlen(self.available_instances)]

        instance_requirements_ram = [[xsum([placement_matrix[type][instance][pod]*self.requirements[pod].ram
                                            for pod in rlen(self.requirements)])
                                      for instance in rlen(self.requirements)]
                                     for type in rlen(self.available_instances)]

        instance_requirements_cpu = [[xsum([placement_matrix[type][instance][pod]*self.requirements[pod].cpu
                                            for pod in rlen(self.requirements)])
                                      for instance in rlen(self.requirements)]
                                     for type in rlen(self.available_instances)]

        model.objective = minimize(xsum([self.available_instances[type].price * instances_in_use[type][instance]
                                         for instance in rlen(self.requirements)
                                         for type in rlen(self.available_instances)]))

        # every pod should be placed exactly one time
        for pod in rlen(self.requirements):
            model += xsum([placement_matrix[type][instance][pod]
                          for instance in rlen(self.requirements)
                          for type in rlen(self.available_instances)]) == 1

        for type in rlen(self.available_instances):
            for instance in rlen(self.requirements):

                #model += self.available_instances[type].ram - instance_requirements_ram[type][instance] <= self.available_instances[type].ram
                #model += self.available_instances[type].cpu - instance_requirements_cpu[type][instance] <= self.available_instances[type].cpu

                for pod in rlen(self.requirements):
                    # fit by ram
                    pass
                    #model += self.available_instances[type].ram >= placement_matrix[type][instance][pod] * requirements[pod].ram

                    # fit by cpu
                    #model += self.available_instances[type].cpu >= placement_matrix[type][instance][pod] * requirements[pod].cpu



        model.optimize()

        print("Result:")

        for type in rlen(self.available_instances):

            print([i.x for i in instances_in_use[type]])
            for instance in rlen(self.requirements):

                if instance_requirements_ram[type][instance].x > 0 or instance_requirements_cpu[type][instance].x > 0:
                    print(f"{self.available_instances[type]} Total booked capacity {instance_requirements_ram[type][instance].x} ram, {instance_requirements_cpu[type][instance].x} cpu")
                    # assert instance_requirements_ram[type][instance].x <= self.available_instances[type].ram
                    # assert instance_requirements_cpu[type][instance].x <= self.available_instances[type].cpu
                    for pod in rlen(self.requirements):
                        if placement_matrix[type][instance][pod].x > 0:
                            print(f"Pod number {pod} {self.requirements[pod]}")

available_instances = [AwsInstanceType(name='big fat', ram=2048, cpu=1, price=162),
                       AwsInstanceType(name='t2.micro', ram=1024, cpu=1, price=0.0162),
                       AwsInstanceType(name='expensive micro', ram=1024, cpu=1, price=0.0163)
                       ]

#available_instances = [AwsInstanceType(name='i3en.3xlarge', ram=98304, cpu=12, price=6.496), AwsInstanceType(name='r5n.12xlarge', ram=393216, cpu=48, price=3.706), AwsInstanceType(name='r5dn.8xlarge', ram=262144, cpu=32, price=2.99732), AwsInstanceType(name='m6id.2xlarge', ram=32768, cpu=8, price=1.5996), AwsInstanceType(name='i2.2xlarge', ram=62464, cpu=8, price=1.972), AwsInstanceType(name='r6g.medium', ram=8192, cpu=1, price=0.0504), AwsInstanceType(name='c6id.8xlarge', ram=65536, cpu=32, price=1.7378), AwsInstanceType(name='m6id.xlarge', ram=16384, cpu=4, price=0.31733), AwsInstanceType(name='m5a.2xlarge', ram=32768, cpu=8, price=0.733), AwsInstanceType(name='d3en.8xlarge', ram=131072, cpu=32, price=9.51776), AwsInstanceType(name='x2iedn.2xlarge', ram=262144, cpu=8, price=1.83398), AwsInstanceType(name='i4i.16xlarge', ram=524288, cpu=64, price=10.066), AwsInstanceType(name='m5n.16xlarge', ram=262144, cpu=64, price=30.982), AwsInstanceType(name='g5.24xlarge', ram=393216, cpu=96, price=8.274), AwsInstanceType(name='r6id.12xlarge', ram=393216, cpu=48, price=3.99168), AwsInstanceType(name='c6i.24xlarge', ram=196608, cpu=96, price=44.904), AwsInstanceType(name='m6id.32xlarge', ram=524288, cpu=128, price=15.6448), AwsInstanceType(name='i4i.metal', ram=1048576, cpu=128, price=13.146), AwsInstanceType(name='m5dn.xlarge', ram=16384, cpu=4, price=0.184), AwsInstanceType(name='r6a.12xlarge', ram=393216, cpu=48, price=5.7408), AwsInstanceType(name='c5d.2xlarge', ram=16384, cpu=8, price=0.65), AwsInstanceType(name='m5ad.2xlarge', ram=32768, cpu=8, price=1.537), AwsInstanceType(name='m5.24xlarge', ram=393216, cpu=96, price=4.608), AwsInstanceType(name='c5ad.xlarge', ram=8192, cpu=4, price=0.373), AwsInstanceType(name='c5n.large', ram=5376, cpu=2, price=0.449), AwsInstanceType(name='t2.micro', ram=1024, cpu=1, price=0.0162), AwsInstanceType(name='c6a.8xlarge', ram=65536, cpu=32, price=1.349), AwsInstanceType(name='m5zn.3xlarge', ram=49152, cpu=12, price=1.2201), AwsInstanceType(name='m5d.24xlarge', ram=393216, cpu=96, price=17.074), AwsInstanceType(name='r5dn.xlarge', ram=32768, cpu=4, price=0.422), AwsInstanceType(name='r5b.large', ram=16384, cpu=2, price=1.741), AwsInstanceType(name='m5n.metal', ram=393216, cpu=96, price=7.474), AwsInstanceType(name='r5n.24xlarge', ram=786432, cpu=96, price=43.152), AwsInstanceType(name='r5dn.metal', ram=786432, cpu=96, price=8.181), AwsInstanceType(name='c5.12xlarge', ram=98304, cpu=48, price=7.93), AwsInstanceType(name='d3.2xlarge', ram=65536, cpu=8, price=2.224), AwsInstanceType(name='c5.large', ram=4096, cpu=2, price=0.662), AwsInstanceType(name='x2idn.32xlarge', ram=2097152, cpu=128, price=28.698), AwsInstanceType(name='c5.metal', ram=196608, cpu=96, price=40.08), AwsInstanceType(name='m5d.12xlarge', ram=196608, cpu=48, price=2.712), AwsInstanceType(name='r5ad.xlarge', ram=32768, cpu=4, price=1.762), AwsInstanceType(name='r6gd.16xlarge', ram=524288, cpu=64, price=3.8114), AwsInstanceType(name='r5n.xlarge', ram=32768, cpu=4, price=1.816), AwsInstanceType(name='x2iezn.12xlarge', ram=1572864, cpu=48, price=10.173), AwsInstanceType(name='c5d.xlarge', ram=8192, cpu=4, price=0.455), AwsInstanceType(name='a1.metal', ram=32768, cpu=16, price=0.408), AwsInstanceType(name='m5zn.metal', ram=196608, cpu=48, price=4.0891), AwsInstanceType(name='x1e.16xlarge', ram=1998848, cpu=64, price=22.358), AwsInstanceType(name='g5.16xlarge', ram=262144, cpu=64, price=4.226), AwsInstanceType(name='r5ad.16xlarge', ram=524288, cpu=64, price=4.609), AwsInstanceType(name='r6a.4xlarge', ram=131072, cpu=16, price=2.91792), AwsInstanceType(name='i4i.large', ram=16384, cpu=2, price=0.189), AwsInstanceType(name='c5.9xlarge', ram=73728, cpu=36, price=1.66), AwsInstanceType(name='m5.2xlarge', ram=32768, cpu=8, price=1.712), AwsInstanceType(name='g3s.xlarge', ram=31232, cpu=4, price=0.898), AwsInstanceType(name='c6id.2xlarge', ram=16384, cpu=8, price=3.44352), AwsInstanceType(name='m6a.24xlarge', ram=393216, cpu=96, price=4.69192), AwsInstanceType(name='x2iedn.32xlarge', ram=4194304, cpu=128, price=42.036), AwsInstanceType(name='r5a.8xlarge', ram=262144, cpu=32, price=13.917), AwsInstanceType(name='r6a.16xlarge', ram=524288, cpu=64, price=7.6544), AwsInstanceType(name='i3en.metal', ram=786432, cpu=96, price=12.47), AwsInstanceType(name='i3.4xlarge', ram=124928, cpu=16, price=1.775), AwsInstanceType(name='u-9tb1.112xlarge', ram=9437184, cpu=448, price=102.508)]

requirements = [
    DeploymentRequirement(ram=2000, cpu=1),
    DeploymentRequirement(ram=100, cpu=0.1),
    DeploymentRequirement(ram=100, cpu=0.2),
]

model = MipModel(available_instances, requirements)
model.calculate()

# ec2 = boto3.resource('ec2', region_name="us-east-1")
# ami_owners = ['056684691971']
# for ami in ec2.images.filter( Owners=ami_owners, Filters=[ {"Name":"description", "Values":["{*}"]} ] ):
#     release_date = None
#     if ami.description is not None:
#         description = json.loads(ami.description)
#         if description is not None:
#             release_date = description["release_date"]
#
#     print(f"{ami.id}, {ami.description}, {release_date}, {ami.tags}")

