# Hash Vote
Welcome a new era of voting unbiased.
# a. Installation:
1. Firstly create a new folder and navigate to the folder.
2. Type ```git clone https://github.com/Krish2208/HashVote``` in the terminal.
3. (Optional) Install conda on your system and form a new virtual enviornment for the HashVote by\
```conda create --name hash-vote```. Now enter the virtual enviornment by typing ```conda activate hash-vote``` in the terminal open at the folder.
4. Install the required packages by typing ```pip install -r requirements.txt``` in the terminal. If pip is not found, install pip as ```conda install pip```.
5. Alternatively run ```conda create --name hash-vote --file requirements.txt``` to create an eviornment with the required packages.
6. Run ```conda install google-auth google-auth-oauthlib``` if facing difficulty with google auth related libraries.
7. Create ```.env``` file with 
    ```
    SECRET_KEY="secret"
    GOOGLE_CLIENT_ID="YOUR GOOGLE CLIENT ID"
    REDIRECT_URI='http://localhost:5000/callback'
    MONGO_URI="YOUR MONGOBD CONNECTION LINK WITH SRV"
    ```
8. To launch the app run ```python main.py```.

# b. Usage:
1. Set up the google auth or login services for your institution.
2. Change the admin ids to required in main.py (line 49).
3. You can now use the app. Admin login ids will be redirected to the admin page and voters to the voting page. Admin can set the voting time, candidates, posts, voters, etc. Which category of voters should vote candidates for which post can also be set. Admn can also edit the voter details, delete votets, etc. 
4. Voters can vote for their favourite candidates securely. Finally the admin can check the validity of the chain and publish the results.
