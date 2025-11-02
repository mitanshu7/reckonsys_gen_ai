## Prep for the assignment:

### Learn async

- [x] https://realpython.com/python-async-features/
- [x] https://realpython.com/async-io-python/

### Decide on which framework to use for async requests (aiohttp vs httpx)


Georges Haidar[^1] makes a good point on how httpx has good ergonomics, the likes of requests. However, Miguel Mendez[^2] provides more insight on the stability/maturity of aiohttp and how it is more suitable for high volume APIs. For this exercise, I will implement async network calls using httpx and scale with aiohttp later.

[^1]: https://www.speakeasy.com/blog/python-http-clients-requests-vs-httpx-vs-aiohttp
[^2]: https://miguel-mendez-ai.com/2024/10/20/aiohttp-vs-httpx