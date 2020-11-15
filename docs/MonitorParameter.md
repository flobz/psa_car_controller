# MonitorParameter

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**extended_event_param** | **list[object]** | Allow to set extra vehicle data (defined in data model) to add to the monitor event when publishing. The possible values are   |value|description|Related model | |----------|:-------------|------:| |vehicle.doorsState|Latest know door state (timestamped)|DoorState| |vehicle.status|Latest know vehicle status (timestamped)|Status| |vehicle.maintenance|Latest know maintenance(timestamped)|Maintenance| |vehicle.position|Last vehicle position (timestamped)|Position| |vehicle.telemetry${.TelemetryEnum}|Latest known telemetry (timestamped). |Telemetry |vehicle.alerts|List of active alerts|Alert|  * For telemetry extension:     * The suffix &#x60;&#x60;&#x60;${.TelemetryEnum}&#x60;&#x60;&#x60; can be selected to refine with telemetry type (from the TelemetryEnum list). This value (with suffix) can be selected **_several times_** to included suitable telemetry messages with the extention.   * Using &#x60;&#x60;&#x60;vehicle.telemetry&#x60;&#x60;&#x60; without suffix means to include all available telemetries.   | [optional] 
**label** | **str** | Monitor lablel (usually its name). | 
**locale** | **str** | Locale is used for rendering text according to language and country for. It should match the  REGEX &#x60;&#x60;&#x60;\\w(-\\w)?&#x60;&#x60;&#x60;. For more details about possible standard values, please refer to [locals list](https://en.wikipedia.org/wiki/Language_localisation).  | [optional] 
**subscribe_param** | [**MonitorSubscribe**](MonitorSubscribe.md) |  | 
**trigger_param** | [**MonitorParameterTriggerParam**](MonitorParameterTriggerParam.md) |  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


