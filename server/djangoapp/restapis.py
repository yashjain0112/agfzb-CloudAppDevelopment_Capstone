""" Djangoapp Rest APIs"""
import json
import requests
from .models import CarDealer, DealerReview


# Create a `get_request` to make HTTP GET requests
API_URL_DEALERSHIP = "https://34dc1aa9-72cc-4904-938b-5b25962a1624-bluemix.cloudant.com/dashboard.html#database/dealerships/b30dabdc430b492cdb56a65bbf5ddb07"
API_URL_REVIEW = 'https://34dc1aa9-72cc-4904-938b-5b25962a1624-bluemix.cloudant.com/dashboard.html#database/reviews/e111f160ef64ba9d7e103ed955da1394'
API_URL_SENTIMENT = 'https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/be2d7df6-2c9b-45d0-9bc5-4e0f8c897ba7'

def get_request(url, **kwargs):
    """ Get """
    try:
        response = requests.get(
            url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        print("Network exception occurred")
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests


def post_request(url, json_payload, **kwargs):
    """ Post"""
    try:
        response = requests.post(url, json=json_payload, params=kwargs)
    except:
        print("Network exception occurred")
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function


def get_dealerships_from_cf():
    """ Get Dealerships"""
    results = []
    json_result = get_request(API_URL_DEALERSHIP)
    if json_result:
        dealerships = json_result["entries"]
        for dealer in dealerships:
            car_dealer = CarDealer(id=dealer["id"],
                                   city=dealer["city"],
                                   state=dealer["state"],
                                   st=dealer["st"],
                                   address=dealer["address"],
                                   zip=dealer["zip"],
                                   lat=dealer["lat"],
                                   long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   full_name=dealer["full_name"])
            results.append(car_dealer)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function


def get_dealer_reviews_from_cf(dealerId):
    """ Get Reviews"""
    results = []
    json_result = get_request(API_URL_REVIEW, dealerId=dealerId)
    if json_result:
        reviews = json_result["entries"]
        for review in reviews:
            sentiment = analyze_review_sentiments(review["review"])
            dealer_review = DealerReview(id=review["id"],
                                         name=review["name"],
                                         dealership=review["dealership"],
                                         review=review["review"],
                                         purchase=review["purchase"],
                                         purchase_date=review["purchase_date"],
                                         car_make=review["car_make"],
                                         car_model=review["car_model"],
                                         car_year=review["car_year"],
                                         sentiment=sentiment)
            results.append(dealer_review)
    return results


def add_dealer_review_to_db(review_post):
    """ Add Review """
    review = {
        "id": review_post['review_id'],
        "name": review_post['reviewer_name'],
        "dealership": review_post['dealership'],
        "review": review_post['review'],
        "purchase": review_post.get('purchase', False),
        "purchase_date": review_post.get('purchase_date'),
        "car_make": review_post.get('car_make'),
        "car_model": review_post.get('car_model'),
        "car_year": review_post.get('car_year')
    }
    return post_request(API_URL_REVIEW, review)

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text


def analyze_review_sentiments(text):
    """ Sentiment Analyze """
    json_result = get_request(API_URL_SENTIMENT, text=text)
    if json_result:
        sentiment_result = json_result.get('label', 'neutral')
    return sentiment_result