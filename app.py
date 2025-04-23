import streamlit as st
import numpy as np
import pickle
import os
from dotenv import load_dotenv
import requests
import json
from newsapi import NewsApiClient
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Fake News Detector & News Recommender",
    page_icon="📰",
    layout="wide"
)

# Initialize NewsAPI client
@st.cache_resource
def get_newsapi_client():
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        st.error("NewsAPI key not found. Please set the NEWS_API_KEY environment variable.")
        return None
    try:
        return NewsApiClient(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing NewsAPI client: {str(e)}")
        return None

def get_news_recommendations(topic):
    try:
        newsapi = get_newsapi_client()
        if newsapi is None:
            return "Error: NewsAPI key not configured properly. Please check your API key."
        
        # Get today's date and date from 7 days ago
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        
        # Search for articles
        articles = newsapi.get_everything(
            q=topic,
            language='en',
            sort_by='relevancy',
            from_param=week_ago.strftime('%Y-%m-%d'),
            to=today.strftime('%Y-%m-%d')
        )
        
        if articles['status'] != 'ok':
            return "Error: Unable to fetch news articles."
            
        # Format the results
        if len(articles['articles']) == 0:
            return f"No recent news articles found about {topic}."
            
        recommendations = f"### Recent News Articles about {topic}:\n\n"
        
        # Take up to 3 articles
        for article in articles['articles'][:3]:
            title = article.get('title', 'No title available')
            description = article.get('description', 'No description available')
            url = article.get('url', '#')
            source = article.get('source', {}).get('name', 'Unknown source')
            date = article.get('publishedAt', '').split('T')[0]
            
            recommendations += f"#### [{title}]({url})\n"
            recommendations += f"**Source:** {source} | **Date:** {date}\n\n"
            recommendations += f"{description}\n\n---\n\n"
            
        return recommendations
    except Exception as e:
        return f"Error getting recommendations: {str(e)}"

def main():
    st.title("📰 Fake News Detector & News Recommender")
    
    try:
        # Create tabs
        tab1, tab2 = st.tabs(["Fake News Detection", "News Recommendations"])
        
        with tab1:
            st.header("Fake News Detection")
            st.info("The machine learning model is currently being set up. Please check back later.")
            
        with tab2:
            st.header("News Recommendations")
            topic = st.text_input("Enter a topic you're interested in:")
            
            if st.button("Get Recommendations"):
                if topic:
                    with st.spinner("Getting recommendations..."):
                        recommendations = get_news_recommendations(topic)
                        st.markdown(recommendations)
                else:
                    st.warning("Please enter a topic to get recommendations.")
    
    except Exception as e:
        st.error("An error occurred while loading the application. Please try refreshing the page.")

if __name__ == "__main__":
    main() 