"""
Script for scraping from cold stream farms website. Single use scraper. Takes ~8 hrs.
"""
import requests
import time
import pickle
from bs4 import BeautifulSoup
from selenium import webdriver
from typing import Union

_TOP_URL = "https://www.coldstreamfarm.net/"
_TREE_URLS_PKL = "../pickles/tree_urls.pkl"
_FILEPATH_TO_CSVS = "../csvs/"
_DRIVER = webdriver.Chrome(executable_path="../chromedriver/macos/chromedriver")


def create_tree_urls(url: str) -> Union[dict, None]:
    """Creates dictionary of trees and associated urls"""
    res = requests.get(url)

    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "html.parser")
        trees = soup.find(
            "ul",
            attrs={
                "class": "product-categories"
            }
        )
        tree_urls = {}
        for item in trees.find_all("a"):
            tree_urls[item.text] = item["href"]
        return tree_urls
    else:
        return


def get_subgroup_tree_urls(tree_urls: dict) -> dict:
    """Returns dict of all tree links in each subgroup if exists"""

    # initialize dictionary to store links
    subgroup_trees = {}

    for tree, url in tree_urls.items():
        time.sleep(10)
        tree_res = requests.get(url)
        if tree_res.status_code == 200:
            print(f"Gathering links for {tree}")
        else:
            print(f"Request couldn't go through for {tree}\n")
            continue

        # use beautiful soup object to parse
        soup = BeautifulSoup(tree_res.content, "html.parser")

        try:
            small_trees = soup.find_all(
                "a",
                {
                    "class": "button product_type_grouped"
                }
            )
            if small_trees:
                for lil_tree in small_trees:
                    tree_name = lil_tree["aria-label"][22:].split('”')[0]
                    subgroup_trees[tree_name] = lil_tree["href"]
            print(f"Link gathering successful for {tree}\n")
        except:
            print(
                f"Link gathering failed for {tree}"
                f"visit: {url}"
            )
            continue
    return subgroup_trees


def scrape_tree_data(tree_url: str, driver=_DRIVER) -> None:
    # load webpage in driver & wait 60 seconds
    driver.get(tree_url)
    time.sleep(60)

    # use soup obj for data grab
    soup_obj = BeautifulSoup(driver.page_source, "html.parser")

    # find tree name for filename
    tree = soup_obj.find("h1").text
    filename = tree.strip() + ".csv"

    # create or open file we will be editing
    f = open(_FILEPATH_TO_CSVS + filename, "w")
    print(f"File created or wiped: {_FILEPATH_TO_CSVS + filename}")

    # find tree name & top of the table
    table = soup_obj.find("tbody")

    # gather headers for given tree
    headers = table.find("tr")
    # create a list to join headers
    list_of_headers = []
    for text in headers.text.split("\n"):
        if len(text.strip()) != 0:
            list_of_headers.append(text.strip())
    # print(",".join(list_of_headers))
    print(f"    Writing headers for {filename}")
    f.write(",".join(list_of_headers))
    f.write("\n")

    # write all rows into csv
    for row in table.find_all("tr")[1:]:
        # gather tree labels, height etc.
        label = row.find(
            "td",
            {
                "class": "woocommerce-grouped-product-list-item__label"
            }
        )
        if label:
            # print(f"{tree} " + label.text.strip() + ",")
            f.write(label.text.strip() + ",")

        # gather pricing info in table
        price = row.find(
            "td",
            {
                "class": "woocommerce-grouped-product-list-item__price"
            }
        )
        if price:
            price_objs = price.find(
                "div",
                {
                    "class": "rp_wcdpd_pricing_table table_right"
                }
            )
            if price_objs:
                cost_per = price_objs.find_all("bdi")
                for price in cost_per:
                    # print(price.text.strip() + ",")
                    f.write(price.text.strip() + ",")

        # gather the out of stock if exists
        stock = row.find(
            "td",
            {
                "class": "woocommerce-grouped-product-list-item__quantity"
            }
        )
        if stock:
            oos = stock.find("p")
            # if there's a p, it's out of stock
            if oos:
                # print(oos.text.strip())
                f.write(oos.text.strip())
            # if there's a div, class quantity then we have a max value we can parse
            has_stock = stock.find("div", {"class": "quantity"})
            if has_stock:
                # print(has_stock.find("input")["max"].strip())
                f.write(has_stock.find("input")["max"].strip())
        f.write("\n")
    f.close()

    # reopen file and store as list to re-write to clean_csvs
    f = open(_FILEPATH_TO_CSVS + filename, "r+")
    lines = f.readlines()
    f.close()
    print(f"Cleaning {filename} and writing to clean_csvs dir:")
    with open("clean_csvs/" + filename, "w") as clean_file:
        for line in lines:
            if line != "\n":
                clean_file.write(line)
    # remove \n at end of clean file to make files match
    f = open("clean_csvs/" + filename, "r+")
    truncate_amt = len(f.read()) - 1
    f.seek(0)
    f.truncate(truncate_amt)
    f.close()
    print(f"Removed newline from EOF in clean_csvs.")
    print(f"Done writing {filename}\n\n")

if __name__ == "__main__":
    tree_urls = create_tree_urls(_TOP_URL)
    if tree_urls:
        tree_url_dict = get_subgroup_tree_urls(tree_urls)
        url_pickle_file = open(_TREE_URLS_PKL, "wb")
        pickle.dump(tree_url_dict, url_pickle_file)
        url_pickle_file.close()
        for tree_url in list(tree_url_dict.values()):
            try:
                scrape_tree_data(tree_url)
            except:
                print(f"    COULD NOT SCRAPE {tree_url}")
                continue

    else:
        print("Unable to gather tree urls - check `create_tree_urls` function.")