import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import nltk

nltk.download('punkt')

st.set_page_config(
    page_title='SHORT_NEWS: A Summarised News📰 Portal',
    page_icon='./Meta/newspaper.ico',
    layout="wide"
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    body {
        background-color: #f4f4f9;
        font-family: 'Arial', sans-serif;
    }
    .title-header {
        font-size: 2.5rem;
        color: #ff4b4b;
        text-align: center;
        font-weight: bold;
        margin-top: 30px;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #444444;
        text-align: center;
        margin-bottom: 50px;
    }
    .category-label {
        font-weight: bold;
        color: #1e88e5;
    }
    .footer {
        font-size: 0.9rem;
        color: #888888;
        text-align: center;
        margin-top: 50px;
    }
    .stExpanderHeader {
        color: #1e88e5;
    }
    .stTextInput, .stSelectbox {
        width: 100%;
        max-width: 600px;
    }
    .card {
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        margin: 20px 0;
        padding: 20px;
    }
    .card h3 {
        color: #ff4b4b;
        font-size: 1.4rem;
        margin-bottom: 10px;
    }
    .card p {
        font-size: 1rem;
        color: #333;
    }
    .card .source {
        font-size: 0.9rem;
        color: #888;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fetch news and job functions (same as before)

def fetch_news_search_topic(topic):
    site = f'https://news.google.com/rss/search?q={topic}'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

def fetch_category_news(topic):
    site = f'https://news.google.com/news/rss/headlines/section/topic/{topic}'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

def resize_image(image, max_width=700):
    width, height = image.size
    aspect_ratio = height / width
    new_width = min(width, max_width)
    new_height = int(new_width * aspect_ratio)
    return image.resize((new_width, new_height))

def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        resized_image = resize_image(image)  # Resize the image
        st.image(resized_image, use_column_width=False)  # Display the resized image
    except:
        image = Image.open('./Meta/no_image.jpg')
        resized_image = resize_image(image)  # Resize default image
        st.image(resized_image, use_column_width=False)  # Display the resized image

# Display news in a card-like layout
def display_news(list_of_news, news_quantity):
    c = 0
    for news in list_of_news:
        c += 1
        st.markdown(f'<div class="card">', unsafe_allow_html=True)
        st.markdown(f"### {news.title.text}", unsafe_allow_html=True)
        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except Exception as e:
            st.error(e)
        fetch_news_poster(news_data.top_image)
        with st.expander(f"Summary: {news.title.text}"):
            st.markdown(
                f"<p style='text-align: justify;'>{news_data.summary}</p>",
                unsafe_allow_html=True
            )
            st.markdown(f"[Read more at {news.source.text}]({news.link.text})")
        st.markdown(f'<p class="source">Published Date: {news.pubDate.text}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if c >= news_quantity:
            break

def run():
    st.markdown("<h1 class='title-header'>InNews🇮🇳: A Summarised News📰 Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Get the latest news, customized for your interests.</p>", unsafe_allow_html=True)

    # Banner Image
    banner_image = Image.open('./Meta/newspaper.png')
    resized_banner_image = resize_image(banner_image, max_width=1000)  # Resize banner image
    st.image(resized_banner_image, use_column_width=False)

    # Sidebar Navigation
    st.sidebar.title("Navigation Menu")
    category = st.sidebar.radio("Select Category", ['Trending🔥 News', 'Favourite💙 Topics', 'Search🔍 Topic'])

    if category == 'Trending🔥 News':
        st.subheader("✅ Trending🔥 News for You")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
        news_list = fetch_top_news()
        display_news(news_list, no_of_news)

    elif category == 'Favourite💙 Topics':
        av_topics = ['WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
        chosen_topic = st.sidebar.selectbox("Choose Your Favourite Topic", av_topics)
        if chosen_topic:
            st.subheader(f"✅ News on {chosen_topic}")
            no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
            news_list = fetch_category_news(chosen_topic)
            if news_list:
                display_news(news_list, no_of_news)
            else:
                st.error(f"No News Found for {chosen_topic}.")

    elif category == 'Search🔍 Topic':
        user_topic = st.sidebar.text_input("Enter Your Topic🔍")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=15, step=1)

        if st.sidebar.button("Search") and user_topic:
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_search_topic(user_topic_pr)
            if news_list:
                st.subheader(f"✅ News on {user_topic.capitalize()}")
                display_news(news_list, no_of_news)
            else:
                st.error(f"No News Found for {user_topic}.")
        else:
            st.warning("Please Enter a Topic to Search.")

    # Footer
    st.markdown("<p class='footer'>InNews © 2025. All Rights Reserved.</p>", unsafe_allow_html=True)

run()
