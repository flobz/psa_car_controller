# psa_connectedcar.VehiclesApi

All URIs are relative to *https://api.groupe-psa.com/connectedcar/v4*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_monitordd**](VehiclesApi.md#delete_monitordd) | **DELETE** /user/vehicles/{id}/monitors/{mid} | Delete a Monitor. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_car_last_position**](VehiclesApi.md#get_car_last_position) | **GET** /user/vehicles/{id}/lastPosition | Last position identified
[**get_telemetry**](VehiclesApi.md#get_telemetry) | **GET** /user/vehicles/{id}/telemetry | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_vehicle_alerts**](VehiclesApi.md#get_vehicle_alerts) | **GET** /user/vehicles/{id}/alerts | 
[**get_vehicle_alerts_by_id**](VehiclesApi.md#get_vehicle_alerts_by_id) | **GET** /user/vehicles/{id}/alerts/{aid} | 
[**get_vehicle_byid**](VehiclesApi.md#get_vehicle_byid) | **GET** /user/vehicles/{id} | Details of vehicule
[**get_vehicle_collision**](VehiclesApi.md#get_vehicle_collision) | **GET** /user/vehicles/{id}/collisions | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_vehicle_collision_by_id**](VehiclesApi.md#get_vehicle_collision_by_id) | **GET** /user/vehicles/{id}/collisions/{cid} | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_vehicle_maintenance**](VehiclesApi.md#get_vehicle_maintenance) | **GET** /user/vehicles/{id}/maintenance | 
[**get_vehicle_monitors**](VehiclesApi.md#get_vehicle_monitors) | **GET** /user/vehicles/{id}/monitors | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_vehicle_monitors_by_id**](VehiclesApi.md#get_vehicle_monitors_by_id) | **GET** /user/vehicles/{id}/monitors/{mid} | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_vehicle_status**](VehiclesApi.md#get_vehicle_status) | **GET** /user/vehicles/{id}/status | Vehicle status.
[**get_vehicles_by_device**](VehiclesApi.md#get_vehicles_by_device) | **GET** /user/vehicles | List of vehicules
[**set_fleet_vehicle_monitor_status**](VehiclesApi.md#set_fleet_vehicle_monitor_status) | **PUT** /user/vehicles/{id}/monitors/{mid}/status | Set a new monitor status. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**set_vehicle_monitor**](VehiclesApi.md#set_vehicle_monitor) | **POST** /user/vehicles/{id}/monitors | Create a new Monitor. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**update_fleet_vehicle_monitor**](VehiclesApi.md#update_fleet_vehicle_monitor) | **PUT** /user/vehicles/{id}/monitors/{mid} | Update and existing Monitor. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE


# **delete_monitordd**
> delete_monitordd(id, mid)

Delete a Monitor. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Stop (disable) an existing Monitor.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
mid = 'mid_example' # str | id of the alert.

try:
    # Delete a Monitor. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_instance.delete_monitordd(id, mid)
except ApiException as e:
    print("Exception when calling VehiclesApi->delete_monitordd: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **mid** | **str**| id of the alert. | 

### Return type

void (empty response body)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_car_last_position**
> Position get_car_last_position(id)

Last position identified

Returns the latest GPS Position of the Vehicle.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.

try:
    # Last position identified
    api_response = api_instance.get_car_last_position(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_car_last_position: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 

### Return type

[**Position**](Position.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/vnd.geo+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_telemetry**
> Telemetry get_telemetry(id, type=type, index_range=index_range, page_size=page_size, page_token=page_token, locale=locale, extension=extension)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the latest Telemetry messages that occurred during a selective timestamp-ranges and bounded by an index range.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
type = ['type_example'] # list[str] | Results will only contain Telemetry messages of this kind. You can add more than one message type. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)
extension = ['extension_example'] # list[str] | Additional data set that will be included in embedded field    * _Disclaimer_:  **Enabling ```maintenance``` extension will automatically disable ```Kinetic``` telemetry message** (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_telemetry(id, type=type, index_range=index_range, page_size=page_size, page_token=page_token, locale=locale, extension=extension)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_telemetry: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **type** | [**list[str]**](str.md)| Results will only contain Telemetry messages of this kind. You can add more than one message type. | [optional] 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **page_size** | **int**| The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   | [optional] [default to 60]
 **page_token** | **str**| Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. | [optional] 
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 
 **extension** | [**list[str]**](str.md)| Additional data set that will be included in embedded field    * _Disclaimer_:  **Enabling &#x60;&#x60;&#x60;maintenance&#x60;&#x60;&#x60; extension will automatically disable &#x60;&#x60;&#x60;Kinetic&#x60;&#x60;&#x60; telemetry message** | [optional] 

### Return type

[**Telemetry**](Telemetry.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_alerts**
> Alerts get_vehicle_alerts(id, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token, locale=locale, locale2=locale2)



Returns the latest alert messages for a Vehicle.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
timestamps = [connected_car_api.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)
locale2 = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. (optional)

try:
    api_response = api_instance.get_vehicle_alerts(id, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token, locale=locale, locale2=locale2)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicle_alerts: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **timestamps** | [**list[TimeRange]**](TimeRange.md)| Array of **\&quot;timestamp\&quot;** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\&quot;timestamp\&quot;** items should be expressed as in &#39;[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)&#39;. | [optional] 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **page_size** | **int**| The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   | [optional] [default to 60]
 **page_token** | **str**| Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. | [optional] 
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 
 **locale2** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. | [optional] 

### Return type

[**Alerts**](Alerts.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_alerts_by_id**
> Alert get_vehicle_alerts_by_id(id, aid, locale=locale)



Returns information about a specific alert messages for a Vehicle.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
aid = 'aid_example' # str | id of the alert.
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)

try:
    api_response = api_instance.get_vehicle_alerts_by_id(id, aid, locale=locale)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicle_alerts_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **aid** | **str**| id of the alert. | 
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 

### Return type

[**Alert**](Alert.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_byid**
> Vehicle get_vehicle_byid(id)

Details of vehicule

Returns detailed information about a Vehicle.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.

try:
    # Details of vehicule
    api_response = api_instance.get_vehicle_byid(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicle_byid: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 

### Return type

[**Vehicle**](Vehicle.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json 

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_collision**
> Collisions get_vehicle_collision(id, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the set of Collisions that occurred for a given vehicle (id) during the timestamp ranges and bounded by an index range.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
timestamps = [connected_car_api.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_vehicle_collision(id, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicle_collision: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **timestamps** | [**list[TimeRange]**](TimeRange.md)| Array of **\&quot;timestamp\&quot;** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\&quot;timestamp\&quot;** items should be expressed as in &#39;[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)&#39;. | [optional] 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **page_size** | **int**| The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   | [optional] [default to 60]
 **page_token** | **str**| Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. | [optional] 

### Return type

[**Collisions**](Collisions.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_collision_by_id**
> Collision get_vehicle_collision_by_id(id, cid)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the Collision that matches the vehicle id and the Collision cid.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
cid = 'cid_example' # str | Results will only contain the Collision related to this Collision *id*.

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_vehicle_collision_by_id(id, cid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicle_collision_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **cid** | **str**| Results will only contain the Collision related to this Collision *id*. | 

### Return type

[**Collision**](Collision.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_maintenance**
> Maintenance get_vehicle_maintenance(id)



Returns the latest Maintenance information for a Vehicle.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.

try:
    api_response = api_instance.get_vehicle_maintenance(id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicle_maintenance: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 

### Return type

[**Maintenance**](Maintenance.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_monitors**
> Monitors get_vehicle_monitors(id, index_range=index_range, page_size=page_size, page_token=page_token)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the list of subscribed Monitors for a Vehicle.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_vehicle_monitors(id, index_range=index_range, page_size=page_size, page_token=page_token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicle_monitors: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **page_size** | **int**| The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   | [optional] [default to 60]
 **page_token** | **str**| Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. | [optional] 

### Return type

[**Monitors**](Monitors.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_monitors_by_id**
> MonitorParameter get_vehicle_monitors_by_id(id, mid)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns information about a specific Monitor for a Vehicle.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
mid = 'mid_example' # str | id of the alert.

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_vehicle_monitors_by_id(id, mid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicle_monitors_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **mid** | **str**| id of the alert. | 

### Return type

[**MonitorParameter**](MonitorParameter.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_status**
> Status get_vehicle_status(id, extension=extension)

Vehicle status.

Returns the latest vehicle status.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
extension = ['extension_example'] # list[str] | Additional data set that will be included in embedded field    * _Disclaimer_:  **Enabling ```odometer``` extension will automatically disable ```kinetic``` telemetry message** (optional)

try:
    # Vehicle status.
    api_response = api_instance.get_vehicle_status(id, extension=extension)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicle_status: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **extension** | [**list[str]**](str.md)| Additional data set that will be included in embedded field    * _Disclaimer_:  **Enabling &#x60;&#x60;&#x60;odometer&#x60;&#x60;&#x60; extension will automatically disable &#x60;&#x60;&#x60;kinetic&#x60;&#x60;&#x60; telemetry message** | [optional] 

### Return type

[**Status**](Status.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicles_by_device**
> Vehicles get_vehicles_by_device(index_range=index_range, page_size=page_size, locale=locale, page_token=page_token)

List of vehicules

Returns the Vehicles associated with the User.

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)

try:
    # List of vehicules
    api_response = api_instance.get_vehicles_by_device(index_range=index_range, page_size=page_size, locale=locale, page_token=page_token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->get_vehicles_by_device: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **page_size** | **int**| The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   | [optional] [default to 60]
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 
 **page_token** | **str**| Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. | [optional] 

### Return type

[**Vehicles**](Vehicles.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json 

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **set_fleet_vehicle_monitor_status**
> MonitorRef set_fleet_vehicle_monitor_status(id, mid, body=body)

Set a new monitor status. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Set monitor status.  

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi()
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
mid = 'mid_example' # str | id of the alert.
body = connected_car_api.MonitorStatusSetter() # MonitorStatusSetter |  (optional)

try:
    # Set a new monitor status. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.set_fleet_vehicle_monitor_status(id, mid, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->set_fleet_vehicle_monitor_status: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **mid** | **str**| id of the alert. | 
 **body** | [**MonitorStatusSetter**](MonitorStatusSetter.md)|  | [optional] 

### Return type

[**MonitorRef**](MonitorRef.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **set_vehicle_monitor**
> MonitorParameter set_vehicle_monitor(id, body=body)

Create a new Monitor. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

>Create a Monitor for a Vehicle. This is a kind of vehicle monitor that generates an event following the transition state of one of the (monitored) data  of the vehicles. As for example the fuel level, the moving out of a defined geographical area.   >When the the trigger occurs, the built event expressed as a JSON object will be sent over the callback. 

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = connected_car_api.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = connected_car_api.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = connected_car_api.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi(connected_car_api.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
body = connected_car_api.MonitorParameter() # MonitorParameter |  (optional)

try:
    # Create a new Monitor. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.set_vehicle_monitor(id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->set_vehicle_monitor: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **body** | [**MonitorParameter**](MonitorParameter.md)|  | [optional] 

### Return type

[**MonitorParameter**](MonitorParameter.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **update_fleet_vehicle_monitor**
> MonitorRef update_fleet_vehicle_monitor(mid, id, body=body)

Update and existing Monitor. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Update an existing ```Monitor``` that has been posted (and accepted previously) for this vehicle. The monitor object (body) provided should be complete because the aggregation is not supported for the update of the ```monitor```. you can retrieve this object using the ```GET /monitor/{mid}``` API then modify it and finally publish it (via this ```PUT API```)  

### Example

```python
from __future__ import print_function
import time
import connected_car_api
from connected_car_api.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = connected_car_api.VehiclesApi()
mid = 'mid_example' # str | id of the alert.
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
body = connected_car_api.MonitorParameter() # MonitorParameter |  (optional)

try:
    # Update and existing Monitor. OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.update_fleet_vehicle_monitor(mid, id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling VehiclesApi->update_fleet_vehicle_monitor: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **mid** | **str**| id of the alert. | 
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **body** | [**MonitorParameter**](MonitorParameter.md)|  | [optional] 

### Return type

[**MonitorRef**](MonitorRef.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

