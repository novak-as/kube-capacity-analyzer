from dataclasses import dataclass

@dataclass
class AwsInstanceType:
    name:str
    ram: int
    cpu: int
    price: float

@dataclass
class DeploymentRequirement:
    ram: int
    cpu: float