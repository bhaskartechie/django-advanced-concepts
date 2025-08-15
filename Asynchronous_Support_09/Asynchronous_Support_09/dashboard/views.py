import httpx
from django.shortcuts import render
from django.views import View
import asyncio

class AsyncPhotoView(View):
    template_name = "dashboard/photos.html"

    async def get(self, request):
        # Example IDs
        photo_ids = list(range(1, 100))
        base_url = "https://jsonplaceholder.typicode.com/photos/"

        async with httpx.AsyncClient() as client:
            # kick off async requests in parallel
            tasks = [client.get(f"{base_url}{pid}") for pid in photo_ids]
            responses = await asyncio.gather(*tasks)

        photos = []
        for resp in responses:
            body = resp.json()
            photos.append(
                {
                    "title": body["title"],
                    "thumbnail": body["thumbnailUrl"],
                    "url": body["url"],
                }
            )

        return render(request, self.template_name, {"photos": photos})

# Normal view (sync)
def photo_view(request):
    import requests
    photo_ids = list(range(1, 100))
    base_url = "https://jsonplaceholder.typicode.com/photos/"

    responses = []
    for pid in photo_ids:
        resp = requests.get(f"{base_url}{pid}")  # <-- synchronous HTTP call
        responses.append(resp.json())

    return render(request, "dashboard/photos.html", {"photos": responses})