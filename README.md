# Inserter

### Overview

The inserter repository is designed to perform asynchronous reading and processing of files containing online conversations, such as posts, comments, and tweets. This repository primarily complements real-time data collection systems by expanding and enriching our dataset using sources from various online datasets. The code execution is optimized using Google Cloud’s GPU infrastructure, which enables fine-grain parallelism. This setup allows us to scale our data quickly and efficiently.

### Key Features

*	Fine-grain parallelism, both process- and thread-based, executed on Google Cloud GPUs allows for rapid dataset expansion.
* Efficiently reads and processes large datasets in the background, without interrupting the real-time data collection processes.
* Enriches existing datasets by adding valuable historical data from offline sources.
* Works with a variety of online conversation datasets, including those from Reddit, Wikipedia, and more.

### Datasets

These are some of the datasets we use with inserter and insert into our own dataset after processing:

* [**Plain Text Wikipedia (Simple English)**](https://www.kaggle.com/datasets/ffatty/plain-text-wikipedia-simpleenglish)
A dataset consisting of plain text from Wikipedia articles written in simple English.
* [**Reddit Russia-Ukraine Conflict**](https://www.kaggle.com/datasets/tariqsays/reddit-russiaukraine-conflict-dataset)
A collection of posts from Reddit covering discussions about the Russia-Ukraine conflict.
* [**Political Reddit Dataset**](https://www.kaggle.com/datasets/nu11us/political-reddit)
A dataset containing political discussions from Reddit.
