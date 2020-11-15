# psa_connectedcar.UserApi

All URIs are relative to *https://api.groupe-psa.com/connectedcar/v4*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_user**](UserApi.md#get_user) | **GET** /user | User&#39;s information


# **get_user**
> User get_user()

User's information

Returns the User's information.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = psa_connectedcar.UserApi()

try:
    # User's information
    api_response = api_instance.get_user()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling UserApi->get_user: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**User**](User.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

