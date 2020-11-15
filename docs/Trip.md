# Trip

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**created_at** | **datetime** | Date when the resource has been created. | [optional] 
**links** | [**TripLinks**](TripLinks.md) |  | [optional] 
**avg_consumption** | [**list[TripAvgConsumption]**](TripAvgConsumption.md) |  | [optional] 
**distance** | **float** | Distance in Km of the trip | [optional] 
**done** | **bool** | Determines whether this trip is finished or not. | [optional] 
**duration** | **str** | Duration of the trip | [optional] 
**faults** | **list[str]** | The faults of this finished or in progress trip. This means that we lacked data from the vehicle to complete the trip description during one of its step (starting, progressing, or finishing). | [optional] 
**id** | **str** | Identifier of a trip | [optional] 
**odometer** | **float** | The mileage of the vehicle at the end of a trip | [optional] 
**start_position** | [**Position**](Position.md) |  | [optional] 
**started_at** | **datetime** | Date &amp; Time when the trip started | [optional] 
**stop_position** | [**Position**](Position.md) |  | [optional] 
**stopped_at** | **datetime** | Date &amp; Time when the trip stopped | [optional] 
**zero_emission_ratio** | **float** | Part of trip distance with zero gaz emission of the trip expressed in percent (0-100%). | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


