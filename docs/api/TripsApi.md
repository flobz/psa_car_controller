# psa_connectedcar.TripsApi

All URIs are relative to *https://api.groupe-psa.com/connectedcar/v4*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_path_for_trip**](TripsApi.md#get_path_for_trip) | **GET** /user/trips/{tid}/wayPoints | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_path_for_trip_0**](TripsApi.md#get_path_for_trip_0) | **GET** /user/vehicles/{id}/trips/{tid}/wayPoints | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_telemetry_for_trip**](TripsApi.md#get_telemetry_for_trip) | **GET** /user/trips/{tid}/telemetry | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_telemetry_for_trip_0**](TripsApi.md#get_telemetry_for_trip_0) | **GET** /user/vehicles/{id}/trips/{tid}/telemetry | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_trip_by_vehicle**](TripsApi.md#get_trip_by_vehicle) | **GET** /user/vehicles/{id}/trips/{tid} | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_trips_by_vehicle**](TripsApi.md#get_trips_by_vehicle) | **GET** /user/trips/{tid} | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_trips_by_vehicle_0**](TripsApi.md#get_trips_by_vehicle_0) | **GET** /user/trips/{tid}/ecoaching | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_trips_by_vehicle_1**](TripsApi.md#get_trips_by_vehicle_1) | **GET** /user/vehicles/{id}/trips | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_trips_by_vehicle_2**](TripsApi.md#get_trips_by_vehicle_2) | **GET** /user/vehicles/{id}/trips/{tid}/ecoaching | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_user_collision_by_tip_by_id**](TripsApi.md#get_user_collision_by_tip_by_id) | **GET** /user/trips/{tid}/collisions/{cid} | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_user_collisions_by_trip_id**](TripsApi.md#get_user_collisions_by_trip_id) | **GET** /user/trips/{tid}/collisions | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_user_trip_alert_by_aid**](TripsApi.md#get_user_trip_alert_by_aid) | **GET** /user/trips/{tid}/alerts/{aid} | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_user_trip_alerts**](TripsApi.md#get_user_trip_alerts) | **GET** /user/trips/{tid}/alerts | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_user_trips**](TripsApi.md#get_user_trips) | **GET** /user/trips | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_vehicle_collision_by_tip_by_id**](TripsApi.md#get_vehicle_collision_by_tip_by_id) | **GET** /user/vehicles/{id}/trips/{tid}/collisions/{cid} | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_vehicle_collisions_by_trip_id**](TripsApi.md#get_vehicle_collisions_by_trip_id) | **GET** /user/vehicles/{id}/trips/{tid}/collisions | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_vehicle_trip_alert_by_aid**](TripsApi.md#get_vehicle_trip_alert_by_aid) | **GET** /user/vehicles/{id}/trips/{tid}/alerts/{aid} | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
[**get_vehicle_trip_alerts**](TripsApi.md#get_vehicle_trip_alerts) | **GET** /user/vehicles/{id}/trips/{tid}/alerts | OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE


# **get_path_for_trip**
> WayPoints get_path_for_trip(tid, index_range=index_range)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Gives the wayPoints for a specified User Trip.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
tid = 'tid_example' # str | the *id* of Trip
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_path_for_trip(tid, index_range=index_range)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_path_for_trip: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tid** | **str**| the *id* of Trip | 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]

### Return type

[**WayPoints**](WayPoints.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_path_for_trip_0**
> WayPoints get_path_for_trip_0(id, tid, index_range=index_range, timestamps=timestamps, tolerance=tolerance)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Gives the Vehicle's wayPoints for a specified Trip.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
tid = 'tid_example' # str | the *id* of Trip
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
timestamps = [psa_connectedcar.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
tolerance = 3.4 # float | Tolerance factor is expressed in length KM unit and is used to simplify path by reducing the total number of points by is using Douglas-Peucker algorithme to find a similar curve with fewer points (find more info here: [Ramer_Douglas_Peucker_algorithm](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm#Algorithm) ).  (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_path_for_trip_0(id, tid, index_range=index_range, timestamps=timestamps, tolerance=tolerance)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_path_for_trip_0: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **tid** | **str**| the *id* of Trip | 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **timestamps** | [**list[TimeRange]**](TimeRange.md)| Array of **\&quot;timestamp\&quot;** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\&quot;timestamp\&quot;** items should be expressed as in &#39;[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)&#39;. | [optional] 
 **tolerance** | **float**| Tolerance factor is expressed in length KM unit and is used to simplify path by reducing the total number of points by is using Douglas-Peucker algorithme to find a similar curve with fewer points (find more info here: [Ramer_Douglas_Peucker_algorithm](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm#Algorithm) ).  | [optional] 

### Return type

[**WayPoints**](WayPoints.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_telemetry_for_trip**
> Telemetry get_telemetry_for_trip(tid, timestamps=timestamps, index_range=index_range, locale=locale, type=type, extension=extension)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the set of Telemetry values that occurred for a given vehicle (id) and a speific Trip (tid) during the timestamp ranges and bounded by an index range.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
tid = 'tid_example' # str | the *id* of Trip
timestamps = [psa_connectedcar.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)
type = ['type_example'] # list[str] | Results will only contain Telemetry messages of this kind. You can add more than one message type. (optional)
extension = ['extension_example'] # list[str] | Additional data set that will be included in embedded field    * _Disclaimer_:  **Enabling ```maintenance``` extension will automatically disable ```Kinetic``` telemetry message** (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_telemetry_for_trip(tid, timestamps=timestamps, index_range=index_range, locale=locale, type=type, extension=extension)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_telemetry_for_trip: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tid** | **str**| the *id* of Trip | 
 **timestamps** | [**list[TimeRange]**](TimeRange.md)| Array of **\&quot;timestamp\&quot;** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\&quot;timestamp\&quot;** items should be expressed as in &#39;[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)&#39;. | [optional] 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 
 **type** | [**list[str]**](str.md)| Results will only contain Telemetry messages of this kind. You can add more than one message type. | [optional] 
 **extension** | [**list[str]**](str.md)| Additional data set that will be included in embedded field    * _Disclaimer_:  **Enabling &#x60;&#x60;&#x60;maintenance&#x60;&#x60;&#x60; extension will automatically disable &#x60;&#x60;&#x60;Kinetic&#x60;&#x60;&#x60; telemetry message** | [optional] 

### Return type

[**Telemetry**](Telemetry.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_telemetry_for_trip_0**
> Telemetry get_telemetry_for_trip_0(id, tid, timestamps=timestamps, index_range=index_range, locale=locale, type=type, extension=extension)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the set of Telemetry values that occurred for a given vehicle (id) and a speific Trip (tid) during the timestamp ranges and bounded by an index range.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
tid = 'tid_example' # str | the *id* of Trip
timestamps = [psa_connectedcar.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)
type = ['type_example'] # list[str] | Results will only contain Telemetry messages of this kind. You can add more than one message type. (optional)
extension = ['extension_example'] # list[str] | Additional data set that will be included in embedded field    * _Disclaimer_:  **Enabling ```maintenance``` extension will automatically disable ```Kinetic``` telemetry message** (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_telemetry_for_trip_0(id, tid, timestamps=timestamps, index_range=index_range, locale=locale, type=type, extension=extension)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_telemetry_for_trip_0: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **tid** | **str**| the *id* of Trip | 
 **timestamps** | [**list[TimeRange]**](TimeRange.md)| Array of **\&quot;timestamp\&quot;** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\&quot;timestamp\&quot;** items should be expressed as in &#39;[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)&#39;. | [optional] 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 
 **type** | [**list[str]**](str.md)| Results will only contain Telemetry messages of this kind. You can add more than one message type. | [optional] 
 **extension** | [**list[str]**](str.md)| Additional data set that will be included in embedded field    * _Disclaimer_:  **Enabling &#x60;&#x60;&#x60;maintenance&#x60;&#x60;&#x60; extension will automatically disable &#x60;&#x60;&#x60;Kinetic&#x60;&#x60;&#x60; telemetry message** | [optional] 

### Return type

[**Telemetry**](Telemetry.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_trip_by_vehicle**
> Trip get_trip_by_vehicle(id, tid)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

This method returns the Trip that matches the Trip id (tid) a given Vehicle (id) has taken.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
tid = 'tid_example' # str | the *id* of Trip

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_trip_by_vehicle(id, tid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_trip_by_vehicle: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **tid** | **str**| the *id* of Trip | 

### Return type

[**Trip**](Trip.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_trips_by_vehicle**
> Trip get_trips_by_vehicle(tid)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

This method returns the Trip that matches the Trip id (tid) User has taken.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
tid = 'tid_example' # str | the *id* of Trip

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_trips_by_vehicle(tid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_trips_by_vehicle: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tid** | **str**| the *id* of Trip | 

### Return type

[**Trip**](Trip.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_trips_by_vehicle_0**
> ECoaching get_trips_by_vehicle_0(tid, locale=locale)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Return the User Trip ECoaching evaluation.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
tid = 'tid_example' # str | the *id* of Trip
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_trips_by_vehicle_0(tid, locale=locale)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_trips_by_vehicle_0: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tid** | **str**| the *id* of Trip | 
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 

### Return type

[**ECoaching**](ECoaching.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_trips_by_vehicle_1**
> Trips get_trips_by_vehicle_1(id, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

This method returns a list of all Trips that a given Vehicle has taken. This will NOT include Trips that have not yet been completed.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
timestamps = [psa_connectedcar.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_trips_by_vehicle_1(id, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_trips_by_vehicle_1: %s\n" % e)
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

[**Trips**](Trips.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_trips_by_vehicle_2**
> ECoaching get_trips_by_vehicle_2(id, tid, locale=locale)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Return the Trip ECoaching evaluation.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
tid = 'tid_example' # str | the *id* of Trip
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_trips_by_vehicle_2(id, tid, locale=locale)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_trips_by_vehicle_2: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **tid** | **str**| the *id* of Trip | 
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 

### Return type

[**ECoaching**](ECoaching.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_user_collision_by_tip_by_id**
> Collision get_user_collision_by_tip_by_id(tid, cid)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the Collision(cid) that occurred for a given vehicle(id) during a Trip(tid) .

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
tid = 'tid_example' # str | the *id* of Trip
cid = 'cid_example' # str | Results will only contain the Collision related to this Collision *id*.

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_user_collision_by_tip_by_id(tid, cid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_user_collision_by_tip_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tid** | **str**| the *id* of Trip | 
 **cid** | **str**| Results will only contain the Collision related to this Collision *id*. | 

### Return type

[**Collision**](Collision.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_user_collisions_by_trip_id**
> Collisions get_user_collisions_by_trip_id(tid, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the set of Collisions that occurred for a given vehicle (id) and a speific Trip (tid) during the timestamp ranges and bounded by an index range.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
tid = 'tid_example' # str | the *id* of Trip
timestamps = [psa_connectedcar.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_user_collisions_by_trip_id(tid, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_user_collisions_by_trip_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tid** | **str**| the *id* of Trip | 
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
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_user_trip_alert_by_aid**
> Alert get_user_trip_alert_by_aid(tid, aid, locale=locale)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns information about a specific alert messages for a given Trip.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
tid = 'tid_example' # str | the *id* of Trip
aid = 'aid_example' # str | id of the alert.
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_user_trip_alert_by_aid(tid, aid, locale=locale)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_user_trip_alert_by_aid: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tid** | **str**| the *id* of Trip | 
 **aid** | **str**| id of the alert. | 
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 

### Return type

[**Alert**](Alert.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_user_trip_alerts**
> Alerts get_user_trip_alerts(tid, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token, locale=locale)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the latest alert messages during a Trip.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
tid = 'tid_example' # str | the *id* of Trip
timestamps = [psa_connectedcar.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_user_trip_alerts(tid, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token, locale=locale)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_user_trip_alerts: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tid** | **str**| the *id* of Trip | 
 **timestamps** | [**list[TimeRange]**](TimeRange.md)| Array of **\&quot;timestamp\&quot;** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\&quot;timestamp\&quot;** items should be expressed as in &#39;[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)&#39;. | [optional] 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **page_size** | **int**| The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   | [optional] [default to 60]
 **page_token** | **str**| Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. | [optional] 
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. | [optional] 

### Return type

[**Alerts**](Alerts.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_user_trips**
> Trips get_user_trips(timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

This method returns a list of all Trips the User has taken. This will NOT include Trips that have not yet been completed.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
timestamps = [psa_connectedcar.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_user_trips(timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_user_trips: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **timestamps** | [**list[TimeRange]**](TimeRange.md)| Array of **\&quot;timestamp\&quot;** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\&quot;timestamp\&quot;** items should be expressed as in &#39;[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)&#39;. | [optional] 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **page_size** | **int**| The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   | [optional] [default to 60]
 **page_token** | **str**| Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. | [optional] 

### Return type

[**Trips**](Trips.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/hal+json

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_collision_by_tip_by_id**
> Collision get_vehicle_collision_by_tip_by_id(id, tid, cid)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the Collision(cid) that occurred for a given vehicle(id) during a Trip(tid) .

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
tid = 'tid_example' # str | the *id* of Trip
cid = 'cid_example' # str | Results will only contain the Collision related to this Collision *id*.

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_vehicle_collision_by_tip_by_id(id, tid, cid)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_vehicle_collision_by_tip_by_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **tid** | **str**| the *id* of Trip | 
 **cid** | **str**| Results will only contain the Collision related to this Collision *id*. | 

### Return type

[**Collision**](Collision.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_collisions_by_trip_id**
> Collisions get_vehicle_collisions_by_trip_id(id, tid, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the set of Collisions that occurred for a given vehicle (id) and a speific Trip (tid) during the timestamp ranges and bounded by an index range.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
tid = 'tid_example' # str | the *id* of Trip
timestamps = [psa_connectedcar.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_vehicle_collisions_by_trip_id(id, tid, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_vehicle_collisions_by_trip_id: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **tid** | **str**| the *id* of Trip | 
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
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_trip_alert_by_aid**
> Alert get_vehicle_trip_alert_by_aid(id, tid, aid, locale=locale)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns information about a specific alert messages for a given Vehicle and Trip.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
tid = 'tid_example' # str | the *id* of Trip
aid = 'aid_example' # str | id of the alert.
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_vehicle_trip_alert_by_aid(id, tid, aid, locale=locale)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_vehicle_trip_alert_by_aid: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **tid** | **str**| the *id* of Trip | 
 **aid** | **str**| id of the alert. | 
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. Respect REGEX \\w(-\\w)? | [optional] 

### Return type

[**Alert**](Alert.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

# **get_vehicle_trip_alerts**
> Alerts get_vehicle_trip_alerts(id, tid, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token, locale=locale)

OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE

Returns the latest alert messages for a Vehicle.

### Example
```python
from __future__ import print_function
import time
import psa_connectedcar
from psa_connectedcar.rest import ApiException
from pprint import pprint

# Configure OAuth2 access token for authorization: Vehicle_auth
configuration = psa_connectedcar.Configuration()
configuration.access_token = 'YOUR_ACCESS_TOKEN'
# Configure API key authorization: client_id
configuration = psa_connectedcar.Configuration()
configuration.api_key['client_id'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['client_id'] = 'Bearer'
# Configure API key authorization: realm
configuration = psa_connectedcar.Configuration()
configuration.api_key['x-introspect-realm'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['x-introspect-realm'] = 'Bearer'

# create an instance of the API class
api_instance = psa_connectedcar.TripsApi(psa_connectedcar.ApiClient(configuration))
id = 'id_example' # str | Results will only be related to this Vehicle *id*.
tid = 'tid_example' # str | the *id* of Trip
timestamps = [psa_connectedcar.TimeRange()] # list[TimeRange] | Array of **\"timestamp\"** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\"timestamp\"** items should be expressed as in '[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)'. (optional)
index_range = '0-' # str | Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 (optional) (default to 0-)
page_size = 60 # int | The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   (optional) (default to 60)
page_token = 'page_token_example' # str | Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. (optional)
locale = 'locale_example' # str | Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. (optional)

try:
    # OUT OF 1ST RELEASE (R-LEV 1.1) SCOPE
    api_response = api_instance.get_vehicle_trip_alerts(id, tid, timestamps=timestamps, index_range=index_range, page_size=page_size, page_token=page_token, locale=locale)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TripsApi->get_vehicle_trip_alerts: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id** | **str**| Results will only be related to this Vehicle *id*. | 
 **tid** | **str**| the *id* of Trip | 
 **timestamps** | [**list[TimeRange]**](TimeRange.md)| Array of **\&quot;timestamp\&quot;** ranges. Results will contain results whose timestamps are included in those date-time ranges (see **timestamp** data  model).**\&quot;timestamp\&quot;** items should be expressed as in &#39;[RFC3339](https://www.ietf.org/rfc/rfc3339.txt)&#39;. | [optional] 
 **index_range** | **str**| Results indexes will be included in this range (see **indexRange** model).      default: 0-    example: 0-, 0-5 | [optional] [default to 0-]
 **page_size** | **int**| The maximum number of results (for a collection results response) to return per page. When not set, at most 60 results will be returned.   | [optional] [default to 60]
 **page_token** | **str**| Start-Page marker, the token for continuing a previous list request on the next page. It is built and used **only** by the server. | [optional] 
 **locale** | **str**| Locale is used for rendering text, correctly displaying regional monetary values, time and date formats. | [optional] 

### Return type

[**Alerts**](Alerts.md)

### Authorization

[Vehicle_auth](../../README.md#Vehicle_auth), [client_id](../../README.md#client_id), [realm](../../README.md#realm)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to Model list]](../../README.md#documentation-for-models) [[Back to README]](../../README.md)

