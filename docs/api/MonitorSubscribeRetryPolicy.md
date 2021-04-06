# MonitorSubscribeRetryPolicy

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**max_retry_number** | **int** | Maximum number of attempts (to be used with retryPolicy set to Bounded). | [optional] 
**policy** | **str** | Defines the retry rules following a WebHook notification failure (ie the return code is not HTTP 2XX). &#39;_None_&#39; means with a single try, &#39;_Bounded_&#39; with a limited number of tries and &#39;_Always_&#39;  with an infinite number of tries.   | 
**retry_delay** | **int** | Time to wait (expressed in seconds) befor retrying to push a notification. | [optional] 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)


