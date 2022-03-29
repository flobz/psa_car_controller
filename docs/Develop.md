# Developer Information
## Contributing

Before create a pull request check your code with Prospector.
You can install it with

```
poetry install --no-root```
#Then in the root of the git project:
prospector
```
## API documentation
The api documentation is described here : [api_spec.md](../api_spec.md).
You can use all functions from the doc, for example :
```myp.api().get_car_last_position(myp.get_vehicle_id_with_vin("myvin"))```
## Analysing request
To analyse the traffics between the app and psa server, you can use mitmproxy.
You will need the client certificate present in the apk at asssets/MWPMYMA1.pfx
```bash
# decrypt the pfx file (there is no password)
openssl pkcs12 -in MWPMYMA1.pfx -out MWPMYMA1.pem -nodes
```
Then you can use mitmproxy for example:

```
mitmproxy --set client_certs=MWPMYMA1.pem
```

For being able to see traffic from the android app you need a rooted phone, you can use an android emulator then follow this:
https://docs.mitmproxy.org/stable/howto-install-system-trusted-ca-android/

