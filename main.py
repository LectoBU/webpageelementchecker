# Script to test web dev assignment by Tim Orman 2016
import webapp2
import cgi
import re
from HTMLParser import HTMLParser

MAIN_PAGE_HTML = """\
<!DOCTYPE html>
<html>
    <head>
        <title>Semantic Element Test</title>
    </head>
    <body>
        <h1>UCWD Semantic ELement Lab Tester</h1>
        <p>Paste you HTML5 Code into the text area below and press submit to see if your code matches what was requested</p>
        <form action="/check" method="post">
            <textarea name="htmltocheck" id="htmltocheck" rows="30" cols="100" placeholder="Place your HTML code here..."></textarea>
            <input type="submit">
            
        </form>
    </body>
</html>"""


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(MAIN_PAGE_HTML)


class CheckDom(webapp2.RequestHandler):
    
        

    def post(self):
            # set up html string to check
            html_string = ""
            myHTML = self.request.get('htmltocheck')
            # strip excess white space
            html_string = re.sub(r'\s\s+', ' ', myHTML)
            # make var to hold messages
            messSTR = ""
            retStr = ""
            
            
            
            
            # instantiate the parser and fed it some HTML
            parser = MyHTMLParser()
            parser.feed(html_string)              
            messSTR = parser.get_message()
            retSTR = "<!DOCTYPE html><html><head><title>Semantic Element Checker</title></head><body><h1>Semantic Element Checker</h1><p><a href='/'>back</a></p><p>" + messSTR + "</p></body></html>"
            
            self.response.write(retSTR)
            
       
        
        
 # create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    # make var to hold messages
    messageSTR = ""
    # make var to hold total elements - needs matching to reqEl dictionary 
    totalreqEl = 15
    # make dictionary to hold requested elements
    reqEl = {}
    reqEl['section'] = 2
    reqEl['header'] = 3
    reqEl['footer'] = 3
    reqEl['article'] = 3
    reqEl['nav'] = 1
    reqEl['aside'] = 1
    reqEl['audio'] = 1
    reqEl['video'] = 1
    # make some counters to check for headers and footers in articles
    articleCount = 0
    headerInArticle = 0
    footerInArticle = 0
    reqheaderInArticle = 3
    reqfooterInArticle = 3

    # make dictionary to hold found tags
    foundEl = {}
    foundEnd = {}
    # make dictionary to hold compared tags
    compareEl = {}
    wellFormed = {}
    # make some vars to hold calculations
    totalScore = 0
    reqElScore = 0
    headerFooterScore = 0
    declScore = 0
    wellFormedScore = 0
    
    def handle_decl(self, decl):
        #print decl    
        if decl == "DOCTYPE html":
            self.declScore = 100.0
            print "decl score = " + str(self.declScore)
            self.messageSTR += "<p>You included the required HTML doctype declaration.</p>"
    def handle_starttag(self, tag, attrs):
        print "Encountered a start tag:", tag
        # checj=k to see if it is a required tag
        if str(tag) in self.reqEl.keys():
            # check to see if element found already
            # print "required element"
            #self.totalEl +=1
            if str(tag) in self.foundEl.keys():
                self.foundEl[str(tag)] += 1
                # print self.foundEl.get(str(tag))
            else:
                self.foundEl[str(tag)] = 1
                # print self.foundEl.get(str(tag))
            #set article open and check header and footer inside element
            if tag == "article":
                self.articleCount += 1
                #print "article = " + str(self.articleCount)
            if tag == "header" and self.articleCount > 0:
                self.headerInArticle += 1
                #print "headerInArticle = " + str(self.headerInArticle)
            if tag == "footer" and self.articleCount > 0:
                self.footerInArticle += 1
                #print "footerInArticle = " + str(self.footerInArticle)

    def handle_endtag(self, tag):
        # print "Encountered an end tag:", tag
        # check to see if it is a required tag
        if str(tag) in self.reqEl.keys():
            if str(tag) in self.foundEnd.keys():
                self.foundEnd[str(tag)] += 1
                # print self.foundEnd.get(str(tag))
            else:
                self.foundEnd[str(tag)] = 1
                # print self.foundEnd.get(str(tag))
            if tag == "article":
                self.articleCount -= 1
                # print "article = " + str(self.articleCount)
                
    def calc_decl(self):
        if(self.declScore == 0.0):
            self.messageSTR += "<p>The required HTML Doctype Declaration was not found<p>"
        self.messageSTR += str('<p>Score for declarations = {:.2%}'.format(self.declScore/100)) + "<p>"
    

    def calc_reqEl(self):
        # print "get_wfmessage message called"
        retMsg = ""
        reqScore = 0.0
        #compareEl = {} 
        # check found elements against required
        for element in self.reqEl:
            if element in self.foundEl.keys():
                self.compareEl[element] =  self.reqEl[element]-self.foundEl[element]
                print "compare element: " + element
                print abs(self.compareEl[element])
                reqScore += abs(self.compareEl[element])
                print "recScore = " + str(reqScore)
                #self.messageSTR += "<p>"str(self.reqEl[element]) + " " + element + "elements were required and you provided " + str(self.foundEl[element]) + "</p>"
                self.messageSTR += "<p>" +str(self.reqEl[element]) + " " + element + " elements were required and you provided " + str(self.foundEl[element]) + "</p>"

            else:
                self.compareEl[element] = None
                print "compare element: " + element
                print self.compareEl[element]
                reqScore += abs(self.reqEl[element])
                print "recScore = " + str(reqScore)
                self.messageSTR += "<p>" +str(self.reqEl[element]) + " " + element + " elements were required and you provided none</p>" 
        self.reqElScore = (1 - (float(reqScore) / float(self.totalreqEl))) * 100
        print "reqElScore = " + str(self.reqElScore)
        self.messageSTR += str('<p>Score for Required Elements = {:.2%}'.format(self.reqElScore/100)) + "<p>"
        
            
    def calc_brokenEl(self):
        wellForm = 0
        # loop through found tags
        for element in self.foundEl:
            #check for empty tags
            if self.check_empty(element) == False:
                print "not empty element"
                if element in self.foundEnd.keys():
                    print "found in foundEnd " + element
                    self.wellFormed[element] = self.foundEl[element] - self.foundEnd[element]
                    if(self.wellFormed[element] != 0):
                        self.messageSTR += "<p>A broken " + element + " element was found. (Note that this issue could be caused by the failure to close an end tag of the previous tag rather than a problem with this element's tags)</p>"
                else:
                    print "not found in end " +  element
                    self.wellFormed[element] = self.foundEl[element]
                    self.messageSTR += "<p>A broken " + element + " element was found. (Note that this issue could be caused by the failure to close an end tag of the previous tag rather than a problem with this element's tags)</p>"
                    #print "calc broken: " + element + " " +  str(self.wellFormed[element])
                    
                wellForm += float(abs(self.wellFormed[element])) / float(self.totalreqEl)
                    #print "wellform score: " + str(wellForm)
        self.wellFormedScore = (1.0-wellForm) * 100
        if len(self.foundEl) == 0:
            self.wellFormedScore = 0.0
        print "wellFormed total = " + str(self.wellFormedScore)
        self.messageSTR += "<p>Score for well formed elements =" + str(' {:.2%}'.format(self.wellFormedScore/100)) + "<p>"
            
                
    def calc_headerFooter(self):
        headerScore = abs(self.reqheaderInArticle - self.headerInArticle)
        footerScore = abs(self.reqfooterInArticle - self.footerInArticle)
        self.headerFooterScore = (1 - (float(headerScore + footerScore) / float(self.reqheaderInArticle + self.reqfooterInArticle))) * 100
        print "header footer score = " + str(self.headerFooterScore)
        self.messageSTR += "<p>" +str(self.reqheaderInArticle) + " header elements contained in article elements were required and you provided " + str(self.headerInArticle) + "</p>"
        self.messageSTR += "<p>" +str(self.reqfooterInArticle) + " footer elements contained in article elements were required and you provided " + str(self.footerInArticle) + "</p>"
        self.messageSTR += "<p>Score for header and footer elements =" + str(' {:.2%}'.format(self.headerFooterScore/100)) + "<p>"
        
    def calc_total(self):
        self.totalScore = float((self.reqElScore + self.headerFooterScore + self.declScore + self.wellFormedScore)/4)
        print "Total score = " + str(self.totalScore)
        self.messageSTR += "<p>Total Score =" + str(' {:.2%}'.format(self.totalScore/100)) + "<p>"
 
          
    def check_empty(self, tag):
        emptyElements = ["link","track","param","area","command","col","base","meta","hr","source","img","keygen","br","wbr","input"]
        if(tag in emptyElements):
            return True
        else:
            return False
    def get_message(self):
        # print "get message called"
        self.calc_decl()
        self.calc_reqEl()
        self.calc_brokenEl()
        self.calc_headerFooter()
        self.foundEl.clear()
        self.foundEnd.clear()
        self.calc_total()
        self.totalEl = 0

        return str(self.messageSTR)
        





app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/check', CheckDom)
], debug=True)
