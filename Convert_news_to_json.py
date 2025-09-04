from dotenv import load_dotenv
import os
from newsapi import NewsApiClient
import json

def convert_news_to_json():
    load_dotenv()
    newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

    top_tech_headlines = newsapi.get_top_headlines(
        country="us",
        category="technology",
        language="en"
    )

    top_sci_headlines = newsapi.get_top_headlines(
        country="us",
        category="science",
        language="en"
    )

    structured_news_data = []

    for i, article in enumerate(top_tech_headlines['articles']):
        structured_news_data.append(
            {
                "id": f"tech_{i}",
                "title": article['title'],
                "source": article['source']['name'],
                "author": article['author'] if article['author'] is not None else "Unknown",
                "date": article['publishedAt'],
                "content": article['description'] if article['description'] is not None else article['title'].split(" - ")[0]
            }
        )

    for i, article in enumerate(top_sci_headlines['articles']):
        structured_news_data.append(
            {
                "id": f"sci_{i}",
                "title": article['title'],
                "source": article['source']['name'],
                "author": article['author'] if article['author'] is not None else "Unknown",
                "date": article['publishedAt'],
                "content": article['description'] if article['description'] is not None else article['title'].split(" - ")[0]
            }
        )

    print(f"Number of articles: {len(structured_news_data)}")

    with open("news_metadata.json", "w") as f:
        for article in structured_news_data:
            json.dump(article, f, ensure_ascii=False)
            f.write("\n")