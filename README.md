# FastAPI OpenID Connect Playground

Learning OpenID Connect in Public

To run the server, set your Doppler secret as an environment variable named `DOPPLER_TOKEN` in Gitpod, scoped to your repository's location.

(In my case, it would be `burningion/fastapi-openid-connect-playground`)

When the project opens, `.gitpod.yml` runs a task that connects to doppler, injects your secrets, and starts up `uvicorn` and FastAPI:

`doppler run -p fastapi-openid-connect-playground -c dev -- -- uvicorn main:app --reload` 

## Generating Secrets for Doppler

The two expected, named secrets are `JWT_SECRET_KEY` and `EXAMPLE_USER_HASHED_PASSWORD`. This repo by default expects your Doppler project to be named `fastapi-openid-connect-playground`, and your environment to be called `dev`. You can change this in the `.gitpod.yaml`, if you search for `doppler run`, where our environment variables stored on Doppler get loaded.

To generate a `JWT_SECRET_KEY` run:

```bash
$ openssl rand -hex 32
```

To generate a hashed password for the `EXAMPLE_USER_HASHED_PASSWORD` run:

```bash
$ python generate_password_hash.py <your-password>
```