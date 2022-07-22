import asyncio
from k8s_requirements import load_info
from aws_prices import describe_available_ec2_instances
from solver import MipModel

if __name__ == "__main__":
    available_instances = list(describe_available_ec2_instances("us-east-1"))
    print(available_instances)

    requirements = asyncio.run(load_info())
    print(requirements)

    model = MipModel(available_instances, requirements)
    model.calculate()
