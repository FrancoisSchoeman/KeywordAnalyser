import os
import requests
import pandas as pd
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

# Load API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def fetch_meta_data(url):
    """
    Fetch meta title and description from the provided URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "N/A"
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        meta_desc = meta_desc['content'] if meta_desc else "N/A"
        return title, meta_desc
    except Exception as e:
        print(f"Error fetching metadata for {url}: {e}")
        return "N/A", "N/A"


def map_relevant_keyword(url, keywords, meta_title, meta_description):
    """
    Use GPT-4 to map the most relevant keyword to the given URL.
    """
    prompt = f"""
    You are a 10-year SEO expert with a proven track record of growing businesses on search organically.
    Based on the following information, select the most relevant keyword for the URL:
    
    URL: {url}
    Current Meta Title: {meta_title}
    Current Meta Description: {meta_description}
    Provided Keywords: {keywords}

    Return the single most relevant keyword from the list based on the URL's content.
    """
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a highly skilled SEO expert."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 100
            },
            headers=headers,
        )
        result = response.json()["choices"][0]["message"]["content"].strip()
        print(f"Mapped Keyword for URL '{url}': {result}")  # Debugging step
        return result
    except Exception as e:
        print(f"Error mapping keyword for URL '{url}': {e}")
        return "N/A"


def fetch_autocomplete_data(keyword):
    """
    Use SERPAPI Autocomplete API to analyze user behavior for the given keyword.
    """
    params = {
        "engine": "google_autocomplete",
        "q": keyword.strip(),
        "api_key": SERPAPI_KEY,
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        suggestions = [item.get("value", "") for item in results.get("suggestions", [])]

        # Debugging step
        print(f"Autocomplete Suggestions for '{keyword}': {suggestions}")

        return suggestions or ["No autocomplete data available"]
    except Exception as e:
        print(f"Error fetching autocomplete data for keyword '{keyword}': {e}")
        return ["Error fetching autocomplete data"]



def parse_gpt_response(result, url):
    """
    Parse GPT-4 response to extract the title, description, and insights.
    """
    try:
        lines = result.split("\n")

        # Extract the new title
        new_title = next((line.split(":")[1].strip() for line in lines if line.startswith("1. SEO Title:")), "N/A")

        # Extract the new description
        new_description = next((line.split(":")[1].strip() for line in lines if line.startswith("2. SEO Description:")), "N/A")

        # Identify the Insights section
        insights_start = next((index for index, line in enumerate(lines) if line.startswith("3. Insights:")), None)
        if insights_start is not None:
            # Extract all lines under Insights that start with '-'
            insights_lines = [
                line.strip() for line in lines[insights_start + 1:] if line.strip().startswith("-")
            ]
            insights = " ".join(insights_lines) if insights_lines else "No insights available."
        else:
            insights = "No insights available."

        # Debugging step
        print(f"Parsed Results for '{url}':")
        print(f"New Title: {new_title}")
        print(f"New Description: {new_description}")
        print(f"Insights: {insights}")

        return new_title, new_description, insights
    except Exception as e:
        print(f"Error parsing GPT-4 response for URL '{url}': {e}")
        return "N/A", "N/A", "Error parsing GPT-4 response"




def generate_seo_content(url, keyword, meta_title, meta_description, autocomplete_data):
    """
    Use GPT-4 to generate a new SEO title, description, and provide insights for a given keyword and URL.
    """
    formatted_autocomplete = "\n".join(autocomplete_data)
    prompt = f"""
    You are a 10-year SEO expert with a proven track record of growing businesses on search organically.
    Based on the following information, provide the output in this exact format:
    
    1. SEO Title: [Your new SEO title]
    2. SEO Description: [Your new SEO description]
    3. Insights:
       - [Bullet point 1 summarizing user behavior or intent]
       - [Bullet point 2 summarizing user behavior or intent]
       - [Additional bullet points, if any]

    URL: {url}
    Current Meta Title: {meta_title}
    Current Meta Description: {meta_description}
    Selected Keyword: {keyword}
    Autocomplete Suggestions (User Search Behavior):
    {formatted_autocomplete}

    The output must strictly follow the format above. Do not change the structure or naming of the sections. Ensure the insights are meaningful and concise, highlighting how users search for services related to the keyword. Observe patterns in the search behaviour to inform optimisation and new meta titles and descriptions and even how the body content must be positioned due to these patterns and observations.
    """
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a highly skilled SEO expert."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500
            },
            headers=headers,
        )
        result = response.json()["choices"][0]["message"]["content"]
        print(f"GPT-4 Response for URL '{url}':\n{result}")  # Debugging step

        # Parse the response
        new_title, new_description, insights = parse_gpt_response(result, url)
        return new_title, new_description, insights

    except Exception as e:
        print(f"Error generating SEO content for URL '{url}': {e}")
        return "N/A", "N/A", "Error parsing GPT-4 response"




def compile_results(urls, keywords):
    """
    Compile results by mapping URLs to the most relevant keywords, fetching autocomplete data,
    and generating SEO content.
    """
    results = []

    for url in urls:
        # Fetch meta data for the URL
        meta_title, meta_description = fetch_meta_data(url)

        # Map the most relevant keyword to the URL
        mapped_keyword = map_relevant_keyword(url, keywords, meta_title, meta_description)
        if mapped_keyword == "N/A":
            continue

        # Fetch autocomplete data for the mapped keyword
        autocomplete_data = fetch_autocomplete_data(mapped_keyword)

        # Generate SEO content
        new_title, new_description, insights = generate_seo_content(
            url, mapped_keyword, meta_title, meta_description, autocomplete_data
        )

        # Append results
        results.append({
            "URL": url,
            "Mapped Keyword": mapped_keyword,
            "Current Title": meta_title,
            "Current Description": meta_description,
            "New SEO Title": new_title,
            "New SEO Description": new_description,
            "Insights": insights,
        })

    return results


def save_to_csv(data, filename="seo_analysis.csv"):
    """
    Save the compiled data to a CSV file.
    """
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")


if __name__ == "__main__":
    # Input
    urls = input("Enter URLs (comma-separated): ").split(",")
    keywords = input("Enter keywords (comma-separated): ").split(",")

    # Compile and save results
    results = compile_results(urls, keywords)
    save_to_csv(results)