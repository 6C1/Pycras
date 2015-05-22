# Pycras

Python CL job listing scraper.

## Usage

1. Update config.conf with your desired location(s), categories, and base uri.
2. `python scraper.py | results.html`
3. Open results in a browser; for example `elinks results.html`

## Jobmail

`jobmail` is a small add-on that will email the results to you. You'll need mail privileges from an http accessible SMTP server.

1. Create a file `mail_config.conf` with your SMTP hostname, port number, from address, and to address. (See `mail_config_example.conf`.)
2. `python jobmail.py`
3. Enter your email password. Look at the source first to make sure it's not getting stolen.
4. Results should show up in your inbox.