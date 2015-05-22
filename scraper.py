'''
    Code for scraping job listings.
'''


from bs4 import BeautifulSoup
from urllib2 import urlopen
from urllib2 import URLError
import re
from datetime import datetime, timedelta
import sys

DEFAULT_LOCATIONS = ["sfbay"]
DEFAULT_CATEGORIES = ['eng']
DEFAULT_URI = "derp"

class Scraper(object):

    def __init__(self, filename=0):

        # Load configuration
        config = self.load_config(filename)

        # Store configuration
        self.locations = map(str, config['locations'])
        self.categories = map(str, config['categories'])
        self.base_uri = str(config['base_uri'])

        # Make a location scraper for each location
        self.scrapers = {
		location : LocationScraper(location, self.categories, self.base_uri) 
		for location in self.locations 
		}


    def scrape(self, location, v=False):
        '''
	    Scrapes a location.
	'''

	self.scrapers[location].scrape(v)


    def scrape_all(self, v=False):
        '''
	    Scrapes all locations.
	'''

	[self.scrape(location, v) for location in self.locations]


    def load_config(self, filename):
        '''
	    Loads configuration file.
	'''
        if not filename:
            return {
                'locations' : DEFAULT_LOCATIONS,
                'categories' : DEFAULT_CATEGORIES,
                'base_uri' : DEFAULT_URI
                }

	try:
            config, cf = {}, {}
	    exec(open(filename).read(), cf)
            config['locations'] = cf['locations'] if 'locations' in cf else DEFAULT_LOCATIONS
            config['categories'] = cf['categories'] if 'categories' in cf else DEFAULT_CATEGORIES
            config['base_uri'] = cf['uri'] if 'uri' in cf else DEFAULT_URI

	    return config
	except Exception as e:
            print "ERROR: {}".format(e.strerror)
	    exit()


    def get_html(self, v=False):

        tag = self.tag
        if v:
            print "Scraping..."
        self.scrape_all(v)

        if v:
            print "Formatting Results..."
        html = tag("h1", "JOB SCRAPER RESULTS")
        
        for location in self.locations:
            html += tag("h2", location)
            for category in self.categories:
                html += tag("h3", category)
                html += "<ul>"
                for post in self.scrapers[location].posts[category]:
                    html += tag("li", self.link(post['url'],post['title']))
                html += "</ul>"

        return html


    def tag(self, tag, text):

        return "<{}>{}</{}>".format(tag, text, tag)

    
    def link(self, href, text):

        return "<a href={} target='_blank'>{}</a>".format(href, text)


class LocationScraper(object):
    '''
	Scraper for a specific location and set of categories
    '''
	
    def __init__(self, location, categories, base_uri):

        self.location = location
        self.categories = categories
        self.base_uri = base_uri

        self.posts = {}
        self.location_name = self.get_location_name()

    
    def scrape(self, v=False):
        '''
	    Scrapes all categories for this location.
	'''

        if 1:
			
            if v:
                print self.location_name.title()
            
            # Get posts for each category
            posts = {
                category : self.get_category_posts(category, v)
                for category in self.categories
                }

            # Save posts
            self.posts = posts


    def get_category_posts(self, category, v=False):
        '''
        Gets posts for single category
        '''
        
        # Construct search URL
        url = "https://{}.{}/search/{}".format(self.location, self.base_uri, category)

        # Open URL, return False on failure.
        try:
            soup = BeautifulSoup(urlopen(url).read())
        except URLError as e:
            print "ERROR @ {} : {}:".format(url, e.reason)
            return 0

        # Get posts
        raw_posts = soup.find_all('p', {'class':'row'})
        # Filter to only today's posts
        filtered_posts = filter(self.date_filter, raw_posts)
        # Get full category name
        full_category_name = soup.find('a', {'class':'reset'}).string

        if v:
            print "\t{}".format(full_category_name.title())

        # Get each post
        posts = [self.get_post(p, category, v) for p in filtered_posts]

        return posts if len(posts) > 0 else 0


    def get_post(self, post, category, v=False):
        '''
            Gets a post.
        '''

        title_link = post.find('a', {'class' : 'hdrlnk'})
        url = 'http://{}.{}{}'.format(self.location, self.base_uri, title_link.get('href'))

        if v:
            print "\t\t{}".format(title_link.get_text())

        # Get post
        try:
            soup = BeautifulSoup(urlopen(url).read())
        except URLError as e:
            print "\t\t\tERROR : {}".format(e.reason)
            return 0

        return self.process_post_soup(soup, url)


    def process_post_soup(self, soup, url):
        '''
            Processes soup object for a post, returns organized post data.
        '''

        title = soup.title.text

        #get the content of the post
        post_content = soup.find('section', {'id':'postingbody'}).text

        #remove repetions of <br> and [/br] at the end of the post
        post_content = re.sub(r'(<br>){2,}','', post_content, flags=re.IGNORECASE)
        post_content = re.sub(r'(</br>){2,}','', post_content, flags=re.IGNORECASE)

        post = {'title' : title,
                'content' : post_content,
                'reply' : 0,
                'url' : url}

        #get the reply email for the post, the info that I need are in another html page
        reply = soup.find('a', {'id':'replylink'})
        if reply is not None:
            reply_link = reply['href']
            reply_url  = url[:url.find('.org/') + 4] + reply_link
            reply_page = BeautifulSoup(urlopen(reply_url).read())
            reply_email = reply_page.find('div', {'class':'anonemail'}).string
            post['reply'] = reply_email

        return post


    def get_location_name(self):
        '''
            Get full name of location.
        '''

        # Construct url
        url = "https://{}.{}".format(self.location, self.base_uri)
        # Load it
        try:
            soup = BeautifulSoup(urlopen(url).read())
        except Exception as e:
            print url, e
            exit()
        # Grab the name
        name = soup.find('h2', {'class' : 'no-mobile'}).get_text()
        return name.title()


    def date_filter(self, post):
        '''
	    Checks if ad was posted today.
	'''
		
        ad_date = post.find('time')['datetime']
        return datetime.now().date() == datetime.strptime(ad_date, '%Y-%m-%d %H:%M').date()


def main() :

    v = len(sys.argv) == 2 and sys.argv[1] == 'v'

    s = Scraper("config.conf")
    
    html = s.get_html(v)
    print BeautifulSoup(html).prettify()

if __name__ == '__main__':
    main()
