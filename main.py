import sys
from lib.data import *
from lib.scraper import *

if __name__ == "__main__":

    brands = ['SKECHERS','ASICSamerica']
    depth = int(sys.argv[1])
    browser_path = str(sys.argv[2])

    option = webdriver.ChromeOptions().add_argument("--incognito")
    browser = webdriver.Chrome(executable_path=browser_path, chrome_options=option)

    for brand in brands:    
        
        scraper = Scraper(brand, depth, browser)
        scraper.get_posts()

        data = Data(scraper)
        data.get_info()

        df = data.get_data()
        df.to_csv("data/{}_posts.csv".format(brand))
        df_product = data.get_product_data()
        df_product.to_csv("data/{}_products.csv".format(brand))

    browser.quit()
