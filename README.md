# UBC Course Scrapping Bot
### Summary: 
This python bot scraps the data from the UBC course website and return which courses have space inside them. This is further implemented with Discord to allow for end users to easily customise the target website and receive notifications when courses have empty seats.

#### Development Status: Finished unless requests are made. Cannot be currently used due to hosting issues.

#### Packages used:
<ul type="">
<li>discord.py</li>
<li>selenium.py</li>
<li>prettytable.py</li>
<li>time.py</li>
<li>asyncio.py</li>
<li>binascii.py</li>
<li>ast.py</li>
<li>logging.py</li>
<li>cryptography.py</li>
</ul>

### How to use:
<ul type="circle">
<!-- 1-->    <li>Create a discord server to keep this bot.</li>
<!-- 2-->    <li>Click this link [https://discord.com/api/oauth2/authorize?client_id=1128102633312370838&permissions=380104817664&scope=bot], and add the bot to the specific server.</li>
<!--2.-->    <li>NOTE: You might want to leave it a private channel near the top for any broadcast or startup messages.</li>
<!-- 3-->    <li>Use the [!setup] command to add an admin.</li>
<!-- 4-->    <li>Add an admin user to the bot to use all commands using [!add-admin:---] replacing the --- with a mention of the user to be made into an admin.</li>
<!-- 5-->    <li>Go to the specific channel where you want to receive pings and start setup by running the [!scrapper] command.<ul type="square"><li>A Scrapper instance will be deleted if it is not used for over 24 hours.</li></ul></li>
<!-- 6-->    <li>Assign the Scrapper an url to check using the [!set-url:---] command replacing the --- with the url, add [&campuscd=UBCO] to specify the Okanagan campus. The url must be a UBC url as the bot only recognises them. This command must not have extra spaces.<ul type = "square"><li>An example would be [!set-url:https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-course&dept=MATH&course=100]</li></ul></li>
<!-- 7-->    <li>Assign the role to ping when space is available using [!set-role:---] where --- is the mention of the role.</li>
<!-- 8-->    <li>At this point you can now run the Scrapper using [!run] if you do not want any more conditions.</li>
<!-- 9-->    <li>Tell the bot if there are labs or discussions in the specific course using [!set-lab:---] where --- is true or false.</li>
<!--10-->    <li>You can further decide if the bot should be on the lookout for some specific sections by using [!set-sec:---] where --- is true or false.<ul type = "square"><li>The bot must have at least one section added now before it can be run, add sections using [!add-sec:---] where --- is the section (Space sensitive).</li><li>Other section specific commands can be found via the [!help] command </li></ul></li>
<!--11-->    <li>Decide if the bot should return the sections where it has restricted space using [!restricted:---] where --- is true or false.</li>
<!--12-->    <li>Decide if the bot should return sections which are Waiting lists with spaces using [!waitlist:---] where --- is true or false.</li>
<!--13-->    <li>Now you can run the bot using [!run]</li>
<!--14-->    <li>If the bot is not needed anymore for that channel stop it using [!stop] and end the instance using [!end].</li>
<!--15-->    <li>When the bot is in a runnable state, you can extract a restart command using [!hash]</li>
<!--16-->    <li>You can repeat the above steps on multiple channels to have them checking for different courses.</li>
</ul>

### If there are any bugs or any requests, please leave a comment on the latest commit.
##### Or in the discord server (There will be a link if it is made/ready).