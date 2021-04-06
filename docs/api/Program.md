# Program

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**occurence** | [**ProgramOccurence**](ProgramOccurence.md) |  | 
**recurrence** | **str** |  Determines the recurrence of the program.  * None: means no recurrence.  * Daily: repeated over the week.  * Weekly: repeated over the weeks of the year from w1 to w52 specified in an array unitary or grouped by ranges (w1, w2,w34-w46, w52).  | [default to 'Daily']
**start** | **str** | The program start time formatted using the duration format based on [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601#Time_intervals) with the schema: P[n]Y[n]M[n]DT[n]H[n]M[n]S  _example_:   * PT14H30M :  14H30min  | 

[[Back to Model list]](../../README.md#documentation-for-models) [[Back to API list]](../../README.md#documentation-for-api-endpoints) [[Back to README]](../../README.md)


