Description
-------------
This package mainly consists of two parts: a web scraper based on Python package selenium (run with `main.py`), and a web application that connects scraped data and certain NLP-related visualization based on Python package dash (run with `app.py`). 

As is asked in the assessment, the two brands scraped in this package is **SKECHERS** and **ASICS**. The web scraper starts with a selenium driver to automate the actions on the main page of the brand, and then acquire the data accordingly. For example, it can click certain elements on the page and then search for the elements of interest that pop up after the click. At the end of scraping, the data will be stored as two csv files for products and brand page resepectively.

With the data acquired, the web application is created to interact with the data, as well as bridge the gap between the summarization model from huggingface.co and the data. So that by clicking certain cells, the generated summarization from the model can be immediately displayed on the page. The web application also includes some visualization based on the text collected from two different web pages.

This package also includes the data schema for the two tables collected from the website, the two tables and their schema are:

**posts**
| id | time | text | image_link | image_flag | video_link | video_flag | products | product_flag |
|----|------|------|------------|------------|------------|------------|----------|--------------|        

As it's shown, the information taken from the scraping is: time, text content, image link, video link, and products link. The flags are prepared for the web application part. 

Since it's not successful to filter out posts about products so far, the product_flag now represents the product-related posts as they redirect to product page directly, while the rest are taken as not related to products.

**product**
| post_id | product_id | brand | product_name | price | details |
|---------|------------|-------|--------------|-------|---------| 

Between these two tables, the foreign key that connects them is `posts.id->product.post_id`, and the primary key for each post in the database is `posts.id` and `product.product_id`. There is also a `schema.sql` file in the `data` folder for reference.

In this package, the previously scraped data are stored as the data source for web application to run without scraping.

The codes in the `lib/` directory are:
 - `scraper.py`: define the `Scraper` object responsible for collecting posts from the page;
 - `data.py`: define the `Data` object that scrapes information from the posts and stores data in the object;
 - `product.py`: define the `Product` that acquires product information and return the data to `product_data` under Data object;
 - `analysis.py`: contain several functions that executes analysis on the data;
 - `utils.py`: contain functions that pre-process text data and the API provided by Huggingface.co to interact with the pre-trained summarization model from Huggingface;

Execution
-------------
*To run the following programs, please make sure your current directory is `Persado_skill_assessment`*

Before running, please make sure you satisfy all the requirements by running:
```
$ pip install -r requirements.txt
```
in your command line

Then, the two main programs can be run separately or sequentially.

* If you want to run the two programs separately, you can run `main.py` with:
```
python3 main.py <depth> <location_of_chrome_webdriver>
```
`<depth>` indicates the smallest number of posts you want to find. `<location_of_chrome_webdriver>` denotes the path to the chromedriver file on your computer. This program will go through pages of two brands to get the data.

* Similarly, you can run `app.py` with:
```
python3 app.py
```
Please make sure it's run with Google Chrome or Safari browser, it usually looks broken on Firefox. This program will open the browser automatically. If the access to open your browser is denied, you can still run the application on `http://localhost:8050`. The two tables on the page corresponds to table **post** and table **product**. And the section under **product** table is the summarization interface. Underneath the data, the two wordcloud figures are generated based on the data scraped most recently.

* To run the two programs sequentially, you can run with the shell script
```
bash run.sh <depth> <location_of_chrome_webdriver>
```
The two arguments are same as the above. And the program can run automatically, starting with `main.py`, and then `app.py`.

*P.S.: python3 can be replaced by python if necessary*