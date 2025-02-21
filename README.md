# Jewel of Bless Network Bot 

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/ccqwe123/jewelOfBless.git bless
   ```
2. Navigate to the project directory:
   ```bash
   cd bless
   ```
4. Install the necessary requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Register to jewel of bless network account first, if you dont have you can register [here](https://bless.network/dashboard).
2. Set and Modify `peer.txt` and `token.txt`. Below how to setup this file.
3. To get your `token/usertoken`, follow this step:
	- Login to your bless account in `https://bless.network/dashboard`, make sure you is in this link (dashboard) before go to next step
	- Go to inspect element, press F12 or right-click then pick inspect element in your browser
	- go to Console tab and paste this 
	```bash
	chrome.storage.local.get("authToken", function(result) {
		console.log(result.authToken);
	});
	```
4. To get your `peer id`, follow this step:
	- Download the [extension](https://chromewebstore.google.com/detail/bless/pljbjcehnhcnofmkdbjolghdcjnmekia)
	- after you download the extension, open `chrome://extensions/?id=pljbjcehnhcnofmkdbjolghdcjnmekia`
  	- open `Developer Tools`, in top right press `Console`.
	- In the console, paste this code:
	```bash
	chrome.storage.local.get("nodeData", function(result) {
		console.log(result.nodeData.peerPubKey);
	});
	```
  	

5. Run the script:
	```bash
	python bless.py
	```

