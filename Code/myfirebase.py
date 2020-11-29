import requests
import json
from kivymd.app import MDApp
from kivymd.toast import toast
from bs4 import BeautifulSoup
import webbrowser
from operator import itemgetter
global amazon_pro
global flipkart_pro
global link_str
amazon_pro = []
flipkart_pro = []
class MyFirebase():
	wak="AIzaSyBuvfAtTzI8FlxaoBcACbnPL7_4Bw2vzIc"
	def sign_up(self,email,password):
		app=MDApp.get_running_app()
		signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wak
		signup_payload={"email":email,"password":password,"returnSecureToken":True}
		sign_up_request=requests.post(signup_url,data=signup_payload)
		sign_up_data=json.loads(sign_up_request.content.decode())
		if sign_up_request.ok==True:
			app.show_popup("Account Created")
			refresh_token=sign_up_data['refreshToken']
			localId=sign_up_data['localId']
			idToken=sign_up_data['idToken']
			with open("refresh_token.txt","w") as f:
				f.write(refresh_token)
			app.local_id=localId
			app.id_token=idToken
			my_data='{"email":"email","password":""}'
			requests.patch("https://bestbuydb-40d9e.firebaseio.com/"+ localId +".json?auth="+ idToken,data=my_data)
			app.change_screen("search_screen")
		if sign_up_request.ok ==False:
			error_data=json.loads(sign_up_request.content.decode())
			error_message=error_data["error"]['message']
			app.show_popup(error_message.replace('_', ' '))
		pass
	def sign_in(self,email,password):
		app=MDApp.get_running_app()
		sign_in_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + self.wak
		sign_in_payload = {"email": email, "password": password, "returnSecureToken": True}
		sign_in_request=requests.post(sign_in_url,data=sign_in_payload)
		sign_in_data=json.loads(sign_in_request.content.decode())
		if sign_in_request.ok==True:
			app.show_popup("Logging In")
			refresh_token=sign_in_data['refreshToken']
			localId=sign_in_data['localId']
			idToken=sign_in_data['idToken']
			with open("refresh_token.txt","w") as f:
				f.write(refresh_token)
			app.local_id=localId
			app.id_token=idToken
			my_data='{"email":"email","password":""}'
			requests.patch("https://bestbuydb-40d9e.firebaseio.com/"+ localId +".json?auth="+ idToken,data=my_data)
			app.change_screen("search_screen")
		if sign_in_request.ok ==False:
			error_data=json.loads(sign_in_request.content.decode())
			error_message=error_data["error"]['message']
			app.show_popup(error_message.replace('_', ' '))
		pass
	def exchange_refresh_token(self,refresh_token):
		refresh_url="https://securetoken.googleapis.com/v1/token?key="+self.wak
		refresh_payload='{"grant_type":"refresh_token","refresh_token":"%s"}' % refresh_token
		refresh_req=requests.post(refresh_url,data=refresh_payload)
		id_token=refresh_req.json()['id_token']
		local_id=refresh_req.json()['user_id']
		return id_token,local_id 
	def reset_pass(self,email):
		app=MDApp.get_running_app()
		reset_pw_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key=" + self.wak
		reset_pw_data = {"email": email, "requestType": "PASSWORD_RESET"} 
		reset_req=requests.post(reset_pw_url,data=reset_pw_data)
		if reset_req.ok==True:
			reset_mssg="Reset password instructions sent to your email."
			app.show_popup(reset_mssg.replace('_', ' '))
		if reset_req.ok ==False:
			error_data=json.loads(reset_req.content.decode())
			error_message=error_data["error"]['message']
			app.show_popup(error_message.replace('_', ' '))
		pass
	def search_product(self,userstr):
		app=MDApp.get_running_app()
		if userstr=="":
			app.change_screen("search_screen")
			app.show_popup("Please enter the Product name")
		else:
			app.show_popup("Searching..")
			app.change_screen("display_screen")
			headers={"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}
			flipkart_url = 'https://www.flipkart.com/search?q={0}'.format(userstr)
			amazon_url = 'https://www.amazon.in/s?k={0}&ref=nb_sb_noss_1'.format(userstr)
			def get_content(url):
				response = requests.get(url, headers=headers)
				soup = BeautifulSoup(response.content, 'html.parser')
				return soup
			def scrape_amazon(url):
				content = get_content(url)
				divs = content.find_all("div", class_="s-include-content-margin s-border-bottom s-latency-cf-section")
				for div in divs:
					try:
						title = div.find('span', class_='a-size-medium a-color-base a-text-normal').string.strip().rsplit(' (',1)[0]
						if title == userstr:
							ratings = div.find('span', class_='a-size-base').string
							if ratings == 'Sponsored':
								ratings = 0
							elif isinstance(ratings, str):
								ratings = ratings.replace(',', '')
							price = div.find('span', class_='a-price-whole').string
							final_price=price.replace(',', '')
							links=div.find('a',class_='a-link-normal a-text-normal')
							extracted_link=links['href']
							final_link="https://www.amazon.in/"+extracted_link
							amazon_pro.append({'title': title, 'ratings': int(ratings), 'price': int(final_price),'link':final_link})
					except AttributeError:
						pass
				scrape_flipkart(flipkart_url)
			def scrape_flipkart(url):
				content = get_content(url)
				divs = content.find_all("div", class_='_1UoZlX')
				for div in divs:
					try:
						title = div.find('div', class_='_3wU53n').string.strip().rsplit(' (',1)[0]
						if title == userstr:
							ratings = div.find('span', class_='_38sUEc').get_text().strip().rsplit(' Ra',2)[0].replace(',', '')
							price = div.find('div', class_='_1vC4OE _2rQ-NK').string.replace('₹', '').replace(',','')
							links=div.find('a', class_='_31qSD5')
							extracted_link=links['href']
							final_link="https://www.flipkart.com"+extracted_link
							flipkart_pro.append({'title': title, 'ratings': int(ratings), 'price': int(price),'link':final_link})
					except AttributeError:
						pass
				amazon_pro.extend(flipkart_pro)
			scrape_amazon(amazon_url)
			def best_products():
				sorted_li = sorted(amazon_pro,key=itemgetter('ratings'),reverse=True)[:1]
				try:
					for d in sorted_li:
						final_list=json.dumps(d, indent=1)
						json.dumps(d, indent=1)
					rating_str=d['ratings']
					price_str=d['price']
					link_str=d['link']
					link_str1=d['link']
					app.root.ids['display_screen'].ids['label1'].text=("[b][color=1E045E]PRODUCT NAME : "+userstr+"[/color][/b]")
					app.root.ids['display_screen'].ids['label2'].text=("[b][color=1E045E]PRODUCT RATINGS : "+str(rating_str)+"[/color][/b]")
					app.root.ids['display_screen'].ids['label3'].text=("[b][color=1E045E]PRODUCT PRICE : "+str(price_str)+"[/color][/b]")
					app.root.ids['display_screen'].ids['label4'].text=("[b][color=1E045E]PRODUCT AVAILABLE IN : "+link_str[12:].rsplit('.com',1)[0].rsplit('.in',1)[0].capitalize()+"[/color][/b]")
					webbrowser.open(link_str1,new=1)
					amazon_pro.clear()
					flipkart_pro.clear()
					pass
				except UnboundLocalError:
					app.change_screen("display_screen")
					app.root.ids['display_screen'].ids['label1'].text=("[b][color=1E045E]Please click on Back Button[/color][/b]")
					app.root.ids['display_screen'].ids['label2'].text=("[b][color=1E045E]Please enter precised Product name[/color][/b]")
					app.root.ids['display_screen'].ids['label3'].text=""
					app.root.ids['display_screen'].ids['label4'].text=""
					pass
			return best_products()
