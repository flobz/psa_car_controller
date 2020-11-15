# MonitorParameterTriggerParam

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**bool_exp** | **str** | A boolean expression that allow defining a logical relationship between triggers. Used Operands with this expression should only be the names of the defined triggers.   Grammar: &#x60;&#x60;&#x60; exp ::&#x3D; exp &#39;&amp;&#39; exp        | exp &#39;|&#39; exp        | (exp)        | !exp &#x60;&#x60;&#x60;  * **example**: having two-zone trigger (two towns) named z1 an z2, one time-trigger (8h00 to 20h00) named t1 and finally three data triggerd named as follow: f(fuel), a(autonomy) , o(odometer).      we can have a boolean expression such as: : &#x60;&#x60;&#x60; ((z1 &amp; t1) | (z2 &amp; !t1) | (f &amp; z1) | (a &amp; (z1|t))  | (o &amp; (z1 | z2))) &#x60;&#x60;&#x60;  | 
**data_triggers** | [**list[DataTrigger]**](DataTrigger.md) | Compound data triggers (will be evaluated with an AND relationship)  *Note*: &#x60;&#x60;&#x60;dataTriggers&#x60;&#x60;&#x60; is depricated according the new monitor spec. Please use the new data schema.  | [optional] 
**time_zone_triggers** | [**TimeZoneTrigger**](TimeZoneTrigger.md) |  | [optional] 
**triggers** | [**list[MonitorTrigger]**](MonitorTrigger.md) | Compound monitor triggers (will be evaluated using boolean expresion :&#x60;&#x60;&#x60;boo.exp&#x60;&#x60;&#x60;)  | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


