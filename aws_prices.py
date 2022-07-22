import boto3
import json
from model import AwsInstanceType

def __get_prices(region):

    pricelist = boto3.client("pricing", region_name=region).get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {"Type": "TERM_MATCH", "Field": "regionCode", "Value": region},
            #{"Type": "TERM_MATCH", "Field": "marketoption", "Value":"OnDemand" },
        ]
    )["PriceList"]

    results = {}

    for product_desc in pricelist:
        product = json.loads(product_desc)

        try:
            family = product["product"]["attributes"]["instanceType"]

            terms = product["terms"]

            if "OnDemand" not in terms:
                continue

            price_info = list(list(terms["OnDemand"].values())[0]["priceDimensions"].values())[0]["pricePerUnit"]

            if "USD" not in price_info:
                continue

            price = float(price_info["USD"])
            if price == 0:
                print(f"Price for {family} is 0. TODO: Verify why")
                continue

            results[family] = price
        except:
            print(product)
            raise

    return results

def describe_available_ec2_instances(region):
    ec2 = boto3.client('ec2', region_name=region)
    describe_args = {

    }

    prices = __get_prices(region)

    while True:
        describe_result = ec2.describe_instance_types(**describe_args)

        for instance in describe_result['InstanceTypes']:

            if instance["InstanceType"] not in prices:
                continue

            yield AwsInstanceType(
                name= instance['InstanceType'],
                ram= instance['MemoryInfo']['SizeInMiB'],
                cpu= instance['VCpuInfo']['DefaultVCpus'],
                price= prices[instance["InstanceType"]])

        if 'NextToken' not in describe_result:
            break
        describe_args['NextToken'] = describe_result['NextToken']