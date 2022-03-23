# Tree Web Scrapers
    Author: Brendan McDonnell
Houses script for scraping tree data.

## How to use this scraper locally
Starting at the top level of your `tree_scraping` directory, follow these instructions to run a new tree scrape.
1. First, create a new python environment using Anaconda:
`conda create --name tree_scrape python=3.7`
2. Once created, activate the environment using conda:
`conda activate tree_scrape`
3. Now you can install the `requirements.txt` in your environment:
```commandline
pip install -r requirements.txt
```

## Caveats
Note that because this employs a headless browser (selenium), be conscious of the loading of the site. You may need to babysit the scraper a bit to make sure the data fully generates before the 60 second sleep is complete.





