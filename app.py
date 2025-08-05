import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def duckduckgo_search(query, num_results=5):
    url = f"https://html.duckduckgo.com/html?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result in soup.select(".result")[:num_results]:
        title_tag = result.select_one("a.result__a")
        snippet_tag = result.select_one(".result__snippet")
        if title_tag and snippet_tag:
            results.append({
                "title": title_tag.text.strip(),
                "snippet": snippet_tag.text.strip(),
                "link": title_tag['href']
            })
    return results

def summarize_results(results):
    text = "\n\n".join(
        f"Title: {r['title']}\nSnippet: {r['snippet']}\nLink: {r['link']}" for r in results
    )
    prompt = f"""Summarize the following web search results into a concise answer:\n\n{text}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

st.set_page_config(page_title="Autonomous Search Bot", layout="centered")
st.title("Autonomous Search Bot")
query = st.text_input("Enter your query:")

if st.button("Search and Summarize"):
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Searching DuckDuckGo..."):
            results = duckduckgo_search(query)

        if results:
            st.success("Results fetched! See below.")
            for r in results:
                st.markdown(f"**[{r['title']}]({r['link']})**\n\n{r['snippet']}")
            st.markdown("Summary")
            st.write(summarize_results(results))
        else:
            st.error("No results found.")
