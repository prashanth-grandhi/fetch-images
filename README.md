Fetch Images
============

This python script downloads images from a web page. Python v2.7.10 used.

## How to execute
If python installation is found in PATH env, simply copy the script to a local directory and execute the script.
Example: python fetchimages.py https://twitter.com

1. Opens a web page URL and fetches all img URLs found in  <img> tags
2. It uses the image URL and downloads image to disk. The image is saved to  temp directory
3. Image URLs of successful downloads are saved to a temp file
4. Debug traces are logged to file FetchImages.log, created in same directory where the script is executed


## Features
1. Handles both absolute and relative image URLs
2. Downloads all supported image formats
3. If image URL path attribute misses filename and extension, such a URL is not processed
4. Error handling
5. Log tracing to file
  

## Design
- Used urllib2 module to open a web page.
- Used re module to match and find all <img> tags
- Used datetime module to generate file name for images
- Used urlparse module construct absolute URL from a relative image URL
- Used tempfile module to save images and URL(s) to temp location on disk
- Used logging module to print trace logs to file
	
Regex used:- re.compile('<[Ii][Mm][Gg](.*[\s]+)[Ss][Rr][Cc][\s]*=[\s]*(")(.*?")')

This matches use cases like:
1. <img src="somelink"..
2. <IMG src="somelink"..
3. <img class="something"  src="somelink"..

