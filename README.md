# CS 7643 Deep Learning Final Project

## Introduction

With social media platforms like TikTok and Instagram reels being used increasingly by today’s generation, these platforms have revolutionized music discovery, changing how music artists are able to reach audiences. Last TikTok hackathon, music discovery from creators to audience was listed as a challenge and is mentioned in TikTok’s main goals for 2025. Our project aims to analyze the relationship between a song’s audio characteristics and its virality on TikTok. We will achieve this by building a deep learning model capable of predicting the popularity score of a song using minimal but information-rich audio features. 

Much prior work uses minimal features (song ‘characteristics’ or metadata like genre or danceability) with classical machine learning approaches or a simple neural network, or using complex features (such as including embeddings of or processing the audio track or lyrics) with complex deep learning networks. The latter often becomes compute-intensive. We plan to investigate a deep learning approach that finds a balance, by producing competitive results using only the aforementioned minimal features (song characteristics) thus requiring less compute power, and a better-architected neural network thus providing a better view of what combinations of song characteristics determine virality. 

Music discovery has increasingly shifted to short-form video platforms like TikTok, where the popularity of a song can explode overnight based on how well it resonates with users. However, predicting which songs will go viral remains largely unpredictable and often relies on trial and error by artists and marketers. If successful, our project would provide a data-driven method to estimate a song's potential for virality based purely on its audio characteristics.

This would give artists, producers, and record labels an early signal of a track’s viral potential before investing heavily in promotion. It would also help platforms like TikTok better recommend emerging songs that are likely to engage users, aligning with their goal of improving music discovery. On a broader scale, it would advance understanding of how certain audio features drive engagement.

By reducing the current randomness in music promotion and giving smaller or independent artists tools traditionally available only through costly marketing campaigns, this project could make the music discovery process more equitable, transparent, and efficient. A successful solution could reshape how songs are marketed and how new music gains visibility globally.

## How to set up project

- Clone the repo.
- Download the preprocessed dataset here: [Google Drive link to dataset](https://drive.google.com/file/d/1LG642eXvzRxJq-UFX-Aqrxdra_4p2dKy/view?usp=sharing)
