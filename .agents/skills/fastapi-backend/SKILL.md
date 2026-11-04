# FastAPI backend

Apply the smallest design that fits the existing service. Read the affected routes, their callers, persistence and tests before changing behavior. Preserve API contracts and data; follow the project's existing layout and security conventions. Do not add layers or dependencies solely to match an example.

- Model request boundaries with appropriate types and Pydantic constraints; use explicit response models when they prevent accidental exposure or clarify a public contract. Keep OpenAPI descriptions and documented error responses consistent with actual behavior.
- Choose `async def` for genuinely asynchronous I/O. Do not run blocking database, file, OCR, or HTTP work on the event loop; use normal synchronous endpoints or the project's threadpool pattern. CPU-heavy work may require a separate worker when load justifies it.
- Use FastAPI dependencies for shared request-scoped concerns such as authentication, authorization, and resource lifecycle when useful. Avoid introducing injectable wrappers for one-off logic. Check authorization on each relevant route and resource.
- Keep HTTP status and response mapping at the API boundary when a real separation helps; preserve the existing error contract and handle expected failures without hiding unexpected ones. Avoid returning secrets or internal details.
- Validate important behavior with focused tests: boundary validation and errors, authorization, and effects on stored data. Use unit tests for isolated logic and integration tests for behavior involving routing, transactions or external services; isolate test state and restore dependency overrides.
- Check configuration, startup/shutdown and migration consequences when affected. Do not silently reset data or assume a deployment environment.

Source: [Auth0, FastAPI Best Practices](https://auth0.com/blog/fastapi-best-practices/) (2026). Its examples are illustrative; verify version-specific behavior against the installed FastAPI/Pydantic versions and official documentation. Favor the existing project's conventions over introducing architecture for its own sake.