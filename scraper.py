import trafilatura

def extract_text_from_url(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        article = trafilatura.extract(downloaded)
        return article
    except:
        return None
