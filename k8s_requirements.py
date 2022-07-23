import os
import asyncio
from model import DeploymentRequirement

# big bad and ugly
class __ParsingMachine:

    def __init__(self, filename):
        self.__content = None
        self.__filename = filename
        self.__position = 0
        self.__states = {
            "search_replicas_section": self.__search_replicas_section,
            "search_containers_section": self.__search_containers_section,
            "search_container_name": self.__search_container_name,
            "search_requests_section": self.__search_requests_section,
            "get_request_cpu": self.__get_request_cpu,
            "get_request_memory": self.__get_request_memory
        }
        self.__current_state = self.__states["search_replicas_section"]

        self.__total_amount = None

        self.__containers = []
        self.__current_container_name = None
        self.__current_request_cpu = None
        self.__current_request_memory = None

    def __dump_container_info(self):
        self.__containers.append((self.__current_container_name, self.__current_request_cpu, self.__current_request_memory))
        self.__current_container_name = None
        self.__current_request_cpu = None
        self.__current_request_memory = None

    def __next_line(self) -> str:
        self.__position += 1
        return self.__content[self.__position - 1]

    def __change_state(self, name):
        # print(f"Change state to {name}")
        self.__current_state = self.__states[name]

    def __search_replicas_section(self):
        line = self.__next_line().rstrip()
        if line.startswith("Replicas:"):
            try:
                self.__total_amount = int(line.split(":")[1].split("|")[2].strip().replace("total", "").strip())
            except Exception as e:
                raise ValueError(line)
            self.__change_state("search_containers_section")

    def __search_containers_section(self):
        line = self.__next_line().lstrip()
        if line.startswith("Containers:"):
            self.__change_state("search_container_name")

    def __search_container_name(self):
        line = self.__next_line()

        if line.startswith("   ") and not line.startswith("    "):
            self.__current_container_name = line.strip()[0:-1]
            self.__change_state("search_requests_section")

    def __search_requests_section(self):
        line = self.__next_line().lstrip()
        if line.startswith("Requests:"):
            self.__change_state("get_request_cpu")

    def __get_request_cpu(self):
        line = self.__next_line()

        self.__current_request_cpu = line.split(":")[1].strip()
        self.__change_state("get_request_memory")

    def __get_request_memory(self):
        line = self.__next_line()
        self.__current_request_memory = line.split(":")[1].strip()
        self.__dump_container_info()

        self.__change_state("search_container_name")

    def __convert_cpu(self, val:str):
        if val.endswith("m"):
            result = int(val[:-1]) * 10**-3
        else:
            result = int(val)

        if result == 0:
            raise ValueError("Cpu requirement is 0")

        return result

    def __convert_memory(self, val:str):
        if val.endswith("Mi"):
            result =  int(val[:-2])
        elif val.endswith("Gi"):
            result = 1024 * int(val[:-2])
        else:
            raise ValueError(f"Unable to parse ram value '{val}'")

        if result == 0:
            raise ValueError(f"Ram requirement is 0")

        return result

    def run(self):

        self.__content = open(self.__filename, "r").readlines()

        while self.__position < len(self.__content):
            self.__current_state()

        total_memory = 0
        total_cpu = 0
        try:

            if len(self.__containers) == 0:
                raise Exception("No containers loaded")

            for (name, cpu, memory) in self.__containers:
                total_cpu += self.__convert_cpu(cpu)
                total_memory += self.__convert_memory(memory)

            for i in range(0, self.__total_amount):
                yield DeploymentRequirement(total_memory, total_cpu)

        except Exception as e:
            print(f"{self.__filename}: {e}")

def __load_all_deployments_list():

    deployments_filename = "deployments.txt"

    if not os.path.exists(f".cache/{deployments_filename}"):
        os.system(f"kubectl get deployments --all-namespaces > .cache/{deployments_filename}")

    with open(f".cache/{deployments_filename}", "r") as deployments_file:
        content = deployments_file.readlines()

        for i in range(1,len(content)):
            namespace_name = content[i][:49].strip()
            deployment_name = content[i][49:106].strip()

            yield (namespace_name, deployment_name)


async def __load_deployment_info(namespace, deployment_name):
    filename = f"{namespace}__{deployment_name}"

    if not os.path.exists(f".cache/descriptions/{filename}"):
        process = await asyncio.create_subprocess_shell(f"kubectl describe deployments {deployment_name} --namespace {namespace} > .cache/descriptions/{filename}")
        await process.wait()
        print(".")



def __parse_deployment(filename):
    with open(f".cache/{filename}", "r") as deployment_file:
        content = deployment_file.readlines()

        for line in content:
            if line.startswith("Replicas:"):
                return line.split(":")[1].split("|")[3].strip()

        raise "Unable to find information about replicas amount"

def __parse_all_descriptions():
    for filename in os.listdir(".cache/descriptions"):
        for requirement in __ParsingMachine(f".cache/descriptions/{filename}").run():
            yield requirement


async def load_info():

    tasks = []
    for (namespace, deployment) in __load_all_deployments_list():
        tasks.append(asyncio.create_task(__load_deployment_info(namespace, deployment)))

        if len(tasks) >= 10:
            await asyncio.gather(*tasks)
            tasks.clear()

    print("All descriptions were downloaded")
    return list(__parse_all_descriptions())



