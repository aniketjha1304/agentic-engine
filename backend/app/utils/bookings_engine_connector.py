import os
import requests
from typing import Dict, Any, List, Optional
from requests.exceptions import HTTPError


class BookingsServiceConnector:
    def __init__(self):
        """
        Initializes the BookingsServiceConnector with
        environment variables for URL, user, and password.
        """
        self.base_url = os.getenv("BOOKINGS_SERVICE_URL")
        self.user = os.getenv("BOOKINGS_SERVICE_USER")
        self.password = os.getenv("BOOKINGS_SERVICE_PASSWORD")

        if not self.base_url:
            raise EnvironmentError(
                "Environment variable for BOOKINGS_SERVICE_URL is missing."
            )

        # Placeholder for authentication (e.g., HTTP Basic Auth)
        self.auth = (self.user, self.password) if self.user and self.password else None

    # Apartments endpoints
    def list_apartments(self, skip: int = 0, limit: int = 100) -> Any:
        """
        Retrieves a list of apartments.

        Parameters
        ----------
        skip : int
            The number of records to skip.
        limit : int
            The maximum number of records to return.

        Returns
        -------
        Any
            A list of apartment records or error details.
        """
        url = f"{self.base_url}/apartments"
        params = {"skip": skip, "limit": limit}
        return self._send_get_request(url, params)

    def get_apartment(self, apartment_id: str) -> Any:
        """
        Retrieves an apartment by its ID.

        Parameters
        ----------
        apartment_id : str
            The ID of the apartment to retrieve.

        Returns
        -------
        Any
            The apartment record or error details.
        """
        url = f"{self.base_url}/apartments/{apartment_id}"
        return self._send_get_request(url)

    def create_apartment(self, apartment_data: Dict[str, Any]) -> Any:
        """
        Creates a new apartment.

        Parameters
        ----------
        apartment_data : Dict[str, Any]
            The data for the new apartment.

        Returns
        -------
        Any
            The created apartment record or error details.
        """
        url = f"{self.base_url}/apartments"
        return self._send_post_request(url, apartment_data)

    def update_apartment(
        self, apartment_id: str, apartment_data: Dict[str, Any]
    ) -> Any:
        """
        Updates an existing apartment.

        Parameters
        ----------
        apartment_id : str
            The ID of the apartment to update.
        apartment_data : Dict[str, Any]
            The updated data for the apartment.

        Returns
        -------
        Any
            The updated apartment record or error details.
        """
        url = f"{self.base_url}/apartments/{apartment_id}"
        return self._send_put_request(url, apartment_data)

    def delete_apartment(self, apartment_id: str) -> Any:
        """
        Deletes an apartment by its ID.

        Parameters
        ----------
        apartment_id : str
            The ID of the apartment to delete.

        Returns
        -------
        Any
            A message indicating success or error details.
        """
        url = f"{self.base_url}/apartments/{apartment_id}"
        return self._send_delete_request(url)

    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Executes a SELECT SQL query on the booking service.

        Parameters
        ----------
        sql_query : str
            The SQL query to execute.

        Returns
        -------
        Dict[str, Any]
            The results of the query.
        """
        url = f"{self.base_url}/execute-query"
        payload = {"sql_query": sql_query}
        response = self._send_post_request(url, payload)
        return response

    # Similar modifications for Customers, Bookings, Cleaning Services, and Cleaning Orders...
    # Customers endpoints
    def list_customers(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves a list of customers.

        Parameters
        ----------
        skip : int
            The number of records to skip.
        limit : int
            The maximum number of records to return.

        Returns
        -------
        List[Dict[str, Any]]
            A list of customer records.
        """
        url = f"{self.base_url}/customers"
        params = {"skip": skip, "limit": limit}
        response = self._send_get_request(url, params)
        return response

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieves a customer by its ID.

        Parameters
        ----------
        customer_id : str
            The ID of the customer to retrieve.

        Returns
        -------
        Dict[str, Any]
            The customer record.
        """
        url = f"{self.base_url}/customers/{customer_id}"
        response = self._send_get_request(url)
        return response

    def search_customers(self, name: str) -> List[Dict[str, Any]]:
        """
        Searches for customers by name.

        Parameters
        ----------
        name : str
            The first name or last name (or part of it) to search for.

        Returns
        -------
        List[Dict[str, Any]]
            A list of matching customer records.
        """
        url = f"{self.base_url}/customers/search"
        params = {"name": name}
        response = self._send_get_request(url, params=params)
        return response

    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new customer.

        Parameters
        ----------
        customer_data : Dict[str, Any]
            The data for the new customer.

        Returns
        -------
        Dict[str, Any]
            The created customer record.
        """
        url = f"{self.base_url}/customers"
        response = self._send_post_request(url, customer_data)
        return response

    def update_customer(
        self, customer_id: str, customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing customer.

        Parameters
        ----------
        customer_id : str
            The ID of the customer to update.
        customer_data : Dict[str, Any]
            The updated data for the customer.

        Returns
        -------
        Dict[str, Any]
            The updated customer record.
        """
        url = f"{self.base_url}/customers/{customer_id}"
        response = self._send_put_request(url, customer_data)
        return response

    def delete_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Deletes a customer by its ID.

        Parameters
        ----------
        customer_id : str
            The ID of the customer to delete.

        Returns
        -------
        Dict[str, Any]
            A message indicating success.
        """
        url = f"{self.base_url}/customers/{customer_id}"
        response = self._send_delete_request(url)
        return response

    # Bookings endpoints
    def list_bookings(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves a list of bookings.

        Parameters
        ----------
        skip : int
            The number of records to skip.
        limit : int
            The maximum number of records to return.

        Returns
        -------
        List[Dict[str, Any]]
            A list of booking records.
        """
        url = f"{self.base_url}/bookings"
        params = {"skip": skip, "limit": limit}
        response = self._send_get_request(url, params)
        return response

    def get_booking(self, booking_id: str) -> Dict[str, Any]:
        """
        Retrieves a booking by its ID.

        Parameters
        ----------
        booking_id : str
            The ID of the booking to retrieve.

        Returns
        -------
        Dict[str, Any]
            The booking record.
        """
        url = f"{self.base_url}/bookings/{booking_id}"
        response = self._send_get_request(url)
        return response

    def create_booking(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new booking.

        Parameters
        ----------
        booking_data : Dict[str, Any]
            The data for the new booking.

        Returns
        -------
        Dict[str, Any]
            The created booking record.
        """
        url = f"{self.base_url}/bookings"
        response = self._send_post_request(url, booking_data)
        return response

    def update_booking(
        self, booking_id: str, booking_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing booking.

        Parameters
        ----------
        booking_id : str
            The ID of the booking to update.
        booking_data : Dict[str, Any]
            The updated data for the booking.

        Returns
        -------
        Dict[str, Any]
            The updated booking record.
        """
        url = f"{self.base_url}/bookings/{booking_id}"
        response = self._send_put_request(url, booking_data)
        return response

    def delete_booking(self, booking_id: str) -> Dict[str, Any]:
        """
        Deletes a booking by its ID.

        Parameters
        ----------
        booking_id : str
            The ID of the booking to delete.

        Returns
        -------
        Dict[str, Any]
            A message indicating success.
        """
        url = f"{self.base_url}/bookings/{booking_id}"
        response = self._send_delete_request(url)
        return response

    # Cleaning Services endpoints
    def list_cleaning_services(
        self, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a list of cleaning services.

        Parameters
        ----------
        skip : int
            The number of records to skip.
        limit : int
            The maximum number of records to return.

        Returns
        -------
        List[Dict[str, Any]]
            A list of cleaning service records.
        """
        url = f"{self.base_url}/cleaning-services"
        params = {"skip": skip, "limit": limit}
        response = self._send_get_request(url, params)
        return response

    def get_cleaning_service(self, cleaning_service_id: str) -> Dict[str, Any]:
        """
        Retrieves a cleaning service by its ID.

        Parameters
        ----------
        cleaning_service_id : str
            The ID of the cleaning service to retrieve.

        Returns
        -------
        Dict[str, Any]
            The cleaning service record.
        """
        url = f"{self.base_url}/cleaning-services/{cleaning_service_id}"
        response = self._send_get_request(url)
        return response

    def create_cleaning_service(
        self, cleaning_service_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a new cleaning service.

        Parameters
        ----------
        cleaning_service_data : Dict[str, Any]
            The data for the new cleaning service.

        Returns
        -------
        Dict[str, Any]
            The created cleaning service record.
        """
        url = f"{self.base_url}/cleaning-services"
        response = self._send_post_request(url, cleaning_service_data)
        return response

    def update_cleaning_service(
        self, cleaning_service_id: str, cleaning_service_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing cleaning service.

        Parameters
        ----------
        cleaning_service_id : str
            The ID of the cleaning service to update.
        cleaning_service_data : Dict[str, Any]
            The updated data for the cleaning service.

        Returns
        -------
        Dict[str, Any]
            The updated cleaning service record.
        """
        url = f"{self.base_url}/cleaning-services/{cleaning_service_id}"
        response = self._send_put_request(url, cleaning_service_data)
        return response

    def delete_cleaning_service(self, cleaning_service_id: str) -> Dict[str, Any]:
        """
        Deletes a cleaning service by its ID.

        Parameters
        ----------
        cleaning_service_id : str
            The ID of the cleaning service to delete.

        Returns
        -------
        Dict[str, Any]
            A message indicating success.
        """
        url = f"{self.base_url}/cleaning-services/{cleaning_service_id}"
        response = self._send_delete_request(url)
        return response

    # Cleaning Orders endpoints
    def list_cleaning_orders(
        self, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieves a list of cleaning orders.

        Parameters
        ----------
        skip : int
            The number of records to skip.
        limit : int
            The maximum number of records to return.

        Returns
        -------
        List[Dict[str, Any]]
            A list of cleaning order records.
        """
        url = f"{self.base_url}/cleaning-orders"
        params = {"skip": skip, "limit": limit}
        response = self._send_get_request(url, params)
        return response

    def get_cleaning_order(self, cleaning_order_id: str) -> Dict[str, Any]:
        """
        Retrieves a cleaning order by its ID.

        Parameters
        ----------
        cleaning_order_id : str
            The ID of the cleaning order to retrieve.

        Returns
        -------
        Dict[str, Any]
            The cleaning order record.
        """
        url = f"{self.base_url}/cleaning-orders/{cleaning_order_id}"
        response = self._send_get_request(url)
        return response

    def create_cleaning_order(
        self, cleaning_order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates a new cleaning order.

        Parameters
        ----------
        cleaning_order_data : Dict[str, Any]
            The data for the new cleaning order.

        Returns
        -------
        Dict[str, Any]
            The created cleaning order record.
        """
        url = f"{self.base_url}/cleaning-orders"
        response = self._send_post_request(url, cleaning_order_data)
        return response

    def update_cleaning_order(
        self, cleaning_order_id: str, cleaning_order_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates an existing cleaning order.

        Parameters
        ----------
        cleaning_order_id : str
            The ID of the cleaning order to update.
        cleaning_order_data : Dict[str, Any]
            The updated data for the cleaning order.

        Returns
        -------
        Dict[str, Any]
            The updated cleaning order record.
        """
        url = f"{self.base_url}/cleaning-orders/{cleaning_order_id}"
        response = self._send_put_request(url, cleaning_order_data)
        return response

    def delete_cleaning_order(self, cleaning_order_id: str) -> Dict[str, Any]:
        """
        Deletes a cleaning order by its ID.

        Parameters
        ----------
        cleaning_order_id : str
            The ID of the cleaning order to delete.

        Returns
        -------
        Dict[str, Any]
            A message indicating success.
        """
        url = f"{self.base_url}/cleaning-orders/{cleaning_order_id}"
        response = self._send_delete_request(url)
        return response

    # Bookings endpoints
    def update_booking(self, booking_id: str, booking_data: Dict[str, Any]) -> Any:
        """
        Updates an existing booking.

        Parameters
        ----------
        booking_id : str
            The ID of the booking to update.
        booking_data : Dict[str, Any]
            The updated data for the booking.

        Returns
        -------
        Any
            The updated booking record or error details.
        """
        url = f"{self.base_url}/bookings/{booking_id}"
        return self._send_put_request(url, booking_data)

    # Apartments endpoints
    def update_apartment(
        self, apartment_id: str, apartment_data: Dict[str, Any]
    ) -> Any:
        """
        Updates an existing apartment.

        Parameters
        ----------
        apartment_id : str
            The ID of the apartment to update.
        apartment_data : Dict[str, Any]
            The updated data for the apartment.

        Returns
        -------
        Any
            The updated apartment record or error details.
        """
        url = f"{self.base_url}/apartments/{apartment_id}"
        return self._send_put_request(url, apartment_data)

    # Customers endpoints
    def update_customer(self, customer_id: str, customer_data: Dict[str, Any]) -> Any:
        """
        Updates an existing customer.

        Parameters
        ----------
        customer_id : str
            The ID of the customer to update.
        customer_data : Dict[str, Any]
            The updated data for the customer.

        Returns
        -------
        Any
            The updated customer record or error details.
        """
        url = f"{self.base_url}/customers/{customer_id}"
        return self._send_put_request(url, customer_data)

    # Cleaning Orders endpoints
    def update_cleaning_order(
        self, cleaning_order_id: str, cleaning_order_data: Dict[str, Any]
    ) -> Any:
        """
        Updates an existing cleaning order.

        Parameters
        ----------
        cleaning_order_id : str
            The ID of the cleaning order to update.
        cleaning_order_data : Dict[str, Any]
            The updated data for the cleaning order.

        Returns
        -------
        Any
            The updated cleaning order record or error details.
        """
        url = f"{self.base_url}/cleaning-orders/{cleaning_order_id}"
        return self._send_put_request(url, cleaning_order_data)

    # Helper methods for HTTP requests
    def _send_get_request(
        self, url: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Sends a GET request to the specified URL with the given parameters.

        Parameters
        ----------
        url : str
            The URL to send the GET request to.
        params : Dict[str, Any], optional
            The query parameters to include in the request.

        Returns
        -------
        Any
            The response JSON from the GET request or error details.

        """
        try:
            response = requests.get(url, params=params, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            # Extract error details from the response
            error_detail = self._extract_error_detail(response)
            return {"error": error_detail}
        except Exception as err:
            return {"error": str(err)}

    def _send_post_request(self, url: str, payload: Dict[str, Any]) -> Any:
        """
        Sends a POST request to the specified URL with the given payload.

        Parameters
        ----------
        url : str
            The URL to send the POST request to.
        payload : Dict[str, Any]
            The JSON payload to send with the request.

        Returns
        -------
        Any
            The response JSON from the POST request or error details.

        """
        try:
            response = requests.post(url, json=payload, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            error_detail = self._extract_error_detail(response)
            return {"error": error_detail}
        except Exception as err:
            return {"error": str(err)}

    def _send_put_request(self, url: str, payload: Dict[str, Any]) -> Any:
        """
        Sends a PUT request to the specified URL with the given payload.

        Parameters
        ----------
        url : str
            The URL to send the PUT request to.
        payload : Dict[str, Any]
            The JSON payload to send with the request.

        Returns
        -------
        Any
            The response JSON from the PUT request or error details.

        """
        try:
            response = requests.put(url, json=payload, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            error_detail = self._extract_error_detail(response)
            return {"error": error_detail}
        except Exception as err:
            return {"error": str(err)}

    def _send_delete_request(self, url: str) -> Any:
        """
        Sends a DELETE request to the specified URL.

        Parameters
        ----------
        url : str
            The URL to send the DELETE request to.

        Returns
        -------
        Any
            The response JSON from the DELETE request or error details.

        """
        try:
            response = requests.delete(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except HTTPError as http_err:
            error_detail = self._extract_error_detail(response)
            return {"error": error_detail}
        except Exception as err:
            return {"error": str(err)}

    def _extract_error_detail(self, response: requests.Response) -> str:
        """
        Extracts the error detail from the response.

        Parameters
        ----------
        response : requests.Response
            The response object from the failed HTTP request.

        Returns
        -------
        str
            The error detail extracted from the response.

        """
        try:
            error_json = response.json()
            if "detail" in error_json:
                return error_json["detail"]
            else:
                return error_json
        except ValueError:
            # Response is not JSON
            return response.text
