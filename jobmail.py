import getpass
import smtplib
from email.mime.text import MIMEText
import scraper


def send_email(msg, to_addr, from_addr, host, port):
    pw = getpass.getpass("Email password:")
    
    msg = MIMEText(msg, 'html')
    msg['subject'] = "Job Scraper Results"
    msg['from'] = "Python Job Scraper"
    msg['to'] = to_addr
    
    print "Connecting to host {}:{}".format(host, port)
    try:
        s = smtplib.SMTP(host, port)
    except Exception as e:
        print e
        exit()
    try:
        s.login(from_addr, pw)
    except:
        print "Invalid username or password."
        exit()
    s.sendmail(from_addr, to_addr, msg.as_string())
    print "Message delivered."
    s.quit()


def main():

    # Get configuration
    config_filename = "mail_config.conf"
    config = {}
    with open(config_filename, "r") as f:
        exec(f.read(), config)
    
    if 'host' in config:
        print "Scraping job listings..."
        s = scraper.Scraper("config.conf")
        msg = s.get_html()
        print "\t\tdone!"
        send_email(msg,
                   config['to_address'],
                   config['from_address'],
                   config['host'],
                   config['port'],)
        

if __name__ == "__main__":
    main()
