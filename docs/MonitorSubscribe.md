# MonitorSubscribe

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**batch_notify** | [**MonitorSubscribeBatchNotify**](MonitorSubscribeBatchNotify.md) |  | [optional] 
**callback** | [**MonitorWebhook**](MonitorWebhook.md) |  | 
**refresh_event** | **float** | Define the period (in sec.) between two refresh events. The refresh-events are sent when the condition of the monitor is satisfied (Trigger -&gt; toggled true).A kind of periodic reminder. | [optional] 
**retry_policy** | [**MonitorSubscribeRetryPolicy**](MonitorSubscribeRetryPolicy.md) |  | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


