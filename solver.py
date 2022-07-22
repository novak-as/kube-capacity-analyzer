from mip import Model, xsum, minimize, BINARY, Var, LinExpr, maximize
from model import DeploymentRequirement, AwsInstanceType
from typing import List
from datetime import datetime

#I'm just lazy to type this everytime
def rlen(something):
    return range(len(something))

class MipModel:

    def __init__(self, available_instances: [AwsInstanceType], requirements: List[DeploymentRequirement]):
        self.available_instances = available_instances
        self.requirements = requirements

    # TODO: this is too slow to be used in the real world 'as is'. some relaxation required.
    #  probably it's worth split-solve-merge instead
    def calculate(self):

        print(f"***********{datetime.now()}*******Begin calculation:")

        model = Model("model")

        # worst-case scenario - we need 1 separate instance for every pod
        placement_matrix = [[[model.add_var(var_type=BINARY)
                       for pod in rlen(self.requirements)]
                       for instance in rlen(self.requirements)]
                       for type in rlen(self.available_instances)]

        instances_in_use = [[model.add_var(var_type=BINARY) for instance in rlen(self.requirements) ]
                            for type in rlen(self.available_instances)]

        instance_requirements_ram = [[xsum([placement_matrix[type][instance][pod]*self.requirements[pod].ram
                                            for pod in rlen(self.requirements)])
                                      for instance in rlen(self.requirements)]
                                     for type in rlen(self.available_instances)]

        instance_requirements_cpu = [[xsum([placement_matrix[type][instance][pod]*self.requirements[pod].cpu
                                            for pod in rlen(self.requirements)])
                                      for instance in rlen(self.requirements)]
                                     for type in rlen(self.available_instances)]

        model.objective = minimize(xsum([(self.available_instances[type].price * instances_in_use[type][instance])
                                         for instance in rlen(self.requirements)
                                         for type in rlen(self.available_instances)]))

        # every pod should be placed exactly one time
        for pod in rlen(self.requirements):
            model += xsum([placement_matrix[type][instance][pod]
                          for instance in rlen(self.requirements)
                          for type in rlen(self.available_instances)]) == 1


        for type in rlen(self.available_instances):
            for instance in rlen(self.requirements):

                model += instance_requirements_ram[type][instance] <= self.available_instances[type].ram
                model += instance_requirements_cpu[type][instance] <= self.available_instances[type].cpu

                # This is actually just `y = 1 if E(x)>0 else 0`
                #  E (x) / n <= y <= (n - 1 + E(x))/n
                model += instances_in_use[type][instance] >= xsum(placement_matrix[type][instance]) / len(self.requirements)
                model += instances_in_use[type][instance] <= (len(self.requirements) - 1 + xsum(placement_matrix[type][instance]))/len(self.requirements)

                for pod in rlen(self.requirements):
                    # fit by ram
                    model += self.available_instances[type].ram >= placement_matrix[type][instance][pod] * self.requirements[pod].ram

                    # fit by cpu
                    model += self.available_instances[type].cpu >= placement_matrix[type][instance][pod] * self.requirements[pod].cpu

        model.optimize()

        print(f"***********{datetime.now()}*******Result:")

        for type in rlen(self.available_instances):

            #print(f"In use: {[i.x for i in instances_in_use[type]]}")
            for instance in rlen(self.requirements):
                #print(f"{[i.x for i in placement_matrix[type][instance]]}")
                if instance_requirements_ram[type][instance].x > 0 or instance_requirements_cpu[type][instance].x > 0:
                    print("")
                    print(f"{self.available_instances[type]} N {instance} Total booked capacity {instance_requirements_ram[type][instance].x} ram, {instance_requirements_cpu[type][instance].x} cpu:")

                    assert instance_requirements_ram[type][instance].x <= self.available_instances[type].ram
                    assert instance_requirements_cpu[type][instance].x <= self.available_instances[type].cpu

                    for pod in rlen(self.requirements):
                        if placement_matrix[type][instance][pod].x > 0:
                            print(f"- Pod number {pod} {self.requirements[pod]}")

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

