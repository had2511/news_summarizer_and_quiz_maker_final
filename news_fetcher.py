import requests

API_KEY = "3fdc3cb3e0ac438cbefbf284aba2f81c"

def fetch_top_headlines(country="us", category="general", page_size=5):
    """
    Fetches top headlines using NewsAPI.
    """
    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"country={country}&category={category}&pageSize={page_size}&apiKey={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    if data.get("status") != "ok":
        print("Error fetching news:", data)
        return []

    articles = []
    for article in data.get("articles", []):
        content = article.get("content") or article.get("description")
        if content:
            articles.append({
                "title": article.get("title"),
                "source": article.get("source", {}).get("name", "Unknown"),
                "content": content,
                "url": article.get("url")
            })
    return articles
