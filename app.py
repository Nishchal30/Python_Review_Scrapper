from flask import Flask, request, render_template, jsonify
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as urReq
import requests

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def home():
    return render_template('index.html')

@app.route('/search', methods = ['POST', 'GET'])
def search():

    if request.method == 'POST':

        try:
            search_for = request.form['search_for'].replace(" ","")
            main_url = "https://www.flipkart.com/search?q=" + search_for

            website_response = urReq(main_url)
            flipkart_data = website_response.read()
            website_response.close()

            beautified_html = bs(flipkart_data, "html.parser")
            all_mobiles = beautified_html.find_all("div", {"class" : "_1AtVbE col-12-12"})
            del all_mobiles[0:2]
            first_mobile = all_mobiles[0]

            mobile_link = "https://www.flipkart.com" + first_mobile.div.div.a['href']
            prodRes = requests.get(mobile_link)
            prodRes.encoding = "utf-8"

            prod_page = bs(prodRes.text, "html.parser")

            all_reviews = prod_page.find_all("div", {"class" : "_16PBlm"})
            

            filename = search_for + ".csv"
            fw = open(filename, "w+", encoding='utf-8')
            headers = "Product, Customer Name, Rating, Heading, Comment, Price, Comment Date \n"
            fw.write(headers)

            reviews = []
            for review in all_reviews:

                try:
                    prod_price = prod_page.find_all("div", {"class" : "_30jeq3 _16Jk6d"})[0].text
                except:
                    prod_price = "No price is given" 

                try:
                    reviewer_name = review.div.div.find_all("p", {"class" : "_2sc7ZR _2V5EHH"})[0].text
                except:
                    reviewer_name = "No name given"

                try:
                    rating = review.div.div.div.div.text      
                except:
                    rating = "No ratings given"

                try:
                    title = review.div.div.div.p.text
                except:
                    title = "No title has given"

                try:
                    comments = review.div.div.find_all("div", {"class" : ""})[0].div.text
                except:
                    comments = "No comments has given"

                try:
                    date_of_comment = review.div.find_all("p", {"class" : "_2sc7ZR"})[1].text
                except:
                    date_of_comment = "No date for comment has gievn"

                mydict = {"Product Price" : prod_price,"Product": search_for, "Name": reviewer_name, "Rating": rating, "CommentHead": title,
                            "Comment": comments, "Comment Date" : date_of_comment}
                
                reviews.append(mydict)
            
                fw.write(str(reviews))
        
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])

        except Exception as e:
                print('The Exception message is: ',e)
                return 'something is wrong'       
    
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)




