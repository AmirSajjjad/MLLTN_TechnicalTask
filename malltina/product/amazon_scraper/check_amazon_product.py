import requests
from bs4 import BeautifulSoup
# from time import sleep
from amazoncaptcha import AmazonCaptcha

from .headers import generate_headers


class AmazonScraperError(Exception):
    def __init__(self, product_code, message):
        self.message = f"ProductCode \"{product_code}\": {message}"
        super().__init__(self.message)


class AmazonScraper:
    def __init__(self) -> None:
        self.error = ""

        self.target_url = "https://www.amazon.com/dp/"
        self.headers = generate_headers()

    def solve_captcha(self, soup):
        for i in range(10):
            image_div = soup.find("div", {"class": "a-row a-text-center"})
            if not image_div:
                return None
            captcha_link = soup.find("div", {"class": "a-row a-text-center"}).img['src']
            captcha = AmazonCaptcha.fromlink(captcha_link)
            solution = captcha.solve()

            amzn = soup.find("input", {"name": "amzn"})['value']
            amzn_r = soup.find("input", {"name": "amzn-r"})['value']

            # sleep(3)
            response = requests.get(
                "https://www.amazon.com/errors/validateCaptcha",
                params={"amzn": amzn, "amzn-r": amzn_r, "field-keywords": solution}, headers=self.headers)
            
            if(response.status_code != 200):
                raise None

            soup = BeautifulSoup(response.text, 'html.parser')

            if "Type the characters you see in this image:" not in response.text:
                return soup

        return None


    def get_title(self, soup):
        title = soup.find('h1',{'id':'title'})
        if title:
            return title.text.lstrip().rstrip()
        else:
            return None
        
    def get_price(self, soup):
        # discount = soup.find("span", attrs={
        #                      "class": "reinventPriceSavingsPercentageMargin savingsPercentage"})
        # priceSpan = soup.select_one(
        #     "span.a-price.reinventPricePriceToPayMargin.priceToPay, span.a-price.apexPriceToPay")

        # # Check to see if there is a price
        # if priceSpan:
        #     price = priceSpan.find(
        #         "span", {"class": "a-offscreen"}).text.strip()
        # else:
        #     price = None

        # # Check to see if there is a discounted price, else just use the normal price or to NA.
        # if discount:
        #     discount = discount.text.strip()
        #     productPrice = soup.find(
        #         "span", attrs={"class": "a-price a-text-price"}).text.strip()
        # elif price:
        #     productPrice = price
        #     discount = False
        # else:
        #     productPrice = "NA"

        # if productPrice == "NA":
        #     otherPriceOption = soup.find("span", {"id": "priceblock_ourprice"})
        #     productPrice = otherPriceOption.text.strip() if otherPriceOption != None else "NA"

        # if productPrice == "NA":
        #     productPrice = soup.find("span", {"class": "a-offscreen"})
        #     productPrice = productPrice.text.strip() if productPrice != None else "NA"

        # if productPrice == "NA":
        #     productPrice = soup.find("span", {"class": "a-price-whole"})
        #     productPrice = productPrice.text.strip() if productPrice != None else "NA"

        price = soup.find("span",{"class":"a-price"})
        if not price:
            return -1
        price = price.find("span")
        if not price:
            return -1
        price = price.text
        price = price.replace("$", "").replace(",", "")
        price = float(price)
        return price

    def get_rating(self, soup):
        rating = soup.find("span",{"id":"acrCustomerReviewText"})
        if rating:
            rating = rating.text
            rating = rating[:rating.find(" ratings")].replace(",", "")
            return rating
        else:
            return -1
    
    def get_score(self, soup):
        score = soup.find("i",{"class":"a-icon-star"})
        if score:
            score = score.text
            score = score[:score.find(" out")]
            score = float(score)
            return score
        else:
            return -1

    def get_product(self, product_code: str) -> dict:
        try:
            response = requests.get(self.target_url + product_code, headers=self.headers)
        except Exception as e:
            raise AmazonScraperError(message=f"FATAL ERROR: {e}", product_code=product_code)

        if(response.status_code == 404):
            return {}
        if(response.status_code != 200):
            raise AmazonScraperError(message=f"status code {response.status_code} != 200", product_code=product_code)
        
        result = {}

        soup = BeautifulSoup(response.text, 'html.parser')

        if "Type the characters you see in this image:" in response.text:
            soup = self.solve_captcha(soup)
            if not soup:
                raise AmazonScraperError(message=f"captcha not solved", product_code=product_code)

        result["title"] = self.get_title(soup)
        if not result["title"]:
            raise AmazonScraperError(message=f"product \"title\" not found", product_code=product_code)
    
        result["price"] = self.get_price(soup)
        if result["price"] == -1:
            raise AmazonScraperError(message=f"product \"price\" not found", product_code=product_code)

        result["rating"] = self.get_rating(soup)
        if result["rating"] == -1:
            raise AmazonScraperError(message=f"product \"rating\" not found", product_code=product_code)

        result["score"] = self.get_score(soup)
        if result["score"] == -1:
            raise AmazonScraperError(message=f"product \"score\" not found", product_code=product_code)

        return result
