from zinc_request_processor import ZincAbstractProcessor

class ZincSimpleOrder(object):
    def __init__(self,
            zinc_base_url="https://api.zinc.io/v0",
            polling_interval= 1.0,
            request_timeout = 180,
            get_request_timeout = 5.0,
            post_request_timeout = 10.0,
            get_request_retries = 3):
        self.processor = ZincAbstractProcessor(zinc_base_url=zinc_base_url,
                polling_interval=polling_interval,
                request_timeout=request_timeout,
                get_request_timeout=get_request_timeout,
                post_request_timeout=post_request_timeout,
                get_request_retries=get_request_retries)

    def process(self, order_details):
        shipping_methods_response = self.processor("shipping_methods", 
                self.shipping_methods_details(order_details))
        store_card_response = self.processor("store_card",
                self.store_card_details(order_details))
        review_order_response = self.processor("review_order", self.review_order_details(
            order_details, shipping_methods_response, store_card_response))
        place_order_response = self.processor("place_order",
                self.place_order_details(order_details, review_order_response))
        return place_order_response

    def shipping_methods_details(self, order_details):
        return {
                "client_token": order_details["client_token"],
                "retailer": order_details["retailer"]
                "shipping_address": order_details["shipping_address"],
                "products": self.products(order_details)
                }

    def store_card_details(self, order_details):
        return {
                "client_token": order_details["client_token"],
                "billing_address": order_details["billing_address"],
                "number": order_details["payment_method"]["number"],
                "expiration_month": order_details["payment_method"]["expiration_month"],
                "expiration_year": order_details["payment_method"]["expiration_year"]
                }

    def review_order_details(self, order_details, shipping_methods_response,
            store_card_response):
        return {
                "client_token": order_details["client_token"],
                "retailer": order_details["retailer"],
                "products": self.products(order_details),
                "shipping_address": order_details["shipping_address"],
                "is_gift": order_details["is_gift"],
                "shipping_method_id": self.shipping_method_id(order_details,
                    shipping_methods_response),
                "payment_method": {
                    "security_code": order_details["payment_method"]["security_code"],
                    "cc_token": store_card_response["cc_token"]
                    }
                "customer_email": order_details["customer_email"]
                }

    def place_order_details(self, order_details, review_order_response):
        return {
                "client_token": order_details["client_token"],
                "place_order_key": review_order_response["place_order_key"]
                }

    def products(self, order_details):
        return [{
            "product_id": order_details["product_id"],
            "quantity": order_details["quantity"]
            }]


    def shipping_method_id(self, order_details, shipping_methods_response):
        return ShippingMethodFactory.shipping_method(
                order_details["shipping_preference"], shipping_methods_response)

class ShippingMethodFactory(object):
    @classmethod
    def shipping_method(klass, shipping_preference, shipping_methods_response):
        if hasattr(klass, shipping_preference):
            return getattr(klass, shipping_preference)(shipping_methods_response)
        else:
            raise TypeError("The shipping preference '%s' is not supported." % shipping_preference)

    @classmethod
    def cheapest(klass, shipping_methods_response):
        minimum = (None, None)
        for method in shipping_methods_response["shipping_methods"]:
            if minimum[0] == None or method["price"] < minimum[0]:
                minimum = (method["price"], method["shipping_method_id"])

        if minimum[0] == None:
            return shipping_methods-response["shipping_methods"][0]["shipping_method_id"]
        else:
            return minimum[1]
