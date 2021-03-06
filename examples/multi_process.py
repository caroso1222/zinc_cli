###############################################################################
#
# ZincSimpleOrder Example
#
# This is an example of how to use the ZincSimpleOrder class to place concurrent
# requests using Python's multiprocessing module. You can place many requests
# at the same time. This example reads in data from "examples/multiple_orders.json".
#
# Note that the example data does not use a valid credit card number, so this
# example will not return correct results.
#
###############################################################################

from multiprocessing import Pool
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'zinc'))
from zinc_simple_order import ZincSimpleOrder
import json
import traceback

FNAME = "dd1"

JSON_IN = FNAME + ".json"
JSON_OUT_FAIL = FNAME + "_fail.json"
JSON_OUT_SUCCESS = FNAME + "_success.json"

class ZincResponse(object):
    def __init__(self, request, response, status):
        self.request = request
        self.response = response
        self.status = status

    def failed(self):
        return self.status == "failed"

    def successful(self):
        return self.status == "successful"

def process_single(order_details):
    if "retailer_credentials" not in order_details.keys():
        order_details["retailer_credentials"] = {}
    simple_order = ZincSimpleOrder()
    try:
        response = simple_order.process(order_details)
        return ZincResponse(order_details, response, "successful")
    except:
        error_message = traceback.format_exc()
        return ZincResponse(order_details, error_message, "failed")

class ZincConcurrentSimpleOrders(object):
    def __init__(self, num_processes=8):
        self.pool = Pool(processes=num_processes)

    def process(self, orders):
        return self.pool.map(process_single, orders)

if __name__ == '__main__':
    filename = "/Users/mkolysh/zinc-file-exchange-parser/data/" + JSON_IN
    failed_filename = "/Users/mkolysh/zinc-file-exchange-parser/data/" + JSON_OUT_FAIL
    success_filename = "/Users/mkolysh/zinc-file-exchange-parser/data/" + JSON_OUT_SUCCESS
    with open(filename, 'rb') as f:
        orders = json.loads(f.read())["orders"]
    print "Number of orders:", len(orders)
    results = ZincConcurrentSimpleOrders().process(orders)

    failed_orders = []
    for result in results:
        if result.failed():
            print result.response
            failed_orders.append(result.request)

    success_orders = []
    for result in results:
        if result.successful():
            print result.response
            success_orders.append(result.request)

    print "Number of failed orders:", len(failed_orders)

    failed_json = {"orders": failed_orders}
    with open(failed_filename, 'wb') as f:
        f.write(json.dumps(failed_json))

    success_json = {"orders": success_orders}
    with open(failed_filename, 'wb') as f:
        f.write(json.dumps(success_json))



