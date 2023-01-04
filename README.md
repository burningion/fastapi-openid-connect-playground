# FastAPI OpenID Connect Playground

Learning OpenID Connect in Public

To run the server, set your doppler secret `DOPPLER_TOKEN` as your project's token, then:

```bash
$ doppler run -p fastapi-openid-connect-playground -- uvicorn main:app --reload
```

`doppler run -p --` will inject your environment variables and secrets into your session from the project named `fastapi-openid-connect-playground` (which might be named differently according to your project). 