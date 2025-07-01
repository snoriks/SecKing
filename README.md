# SECKING 👑

##### **SecKing** is a powerful **security Discord bot** that leverages **Hugging Face AI** models for intelligent moderation, using different models for increased precision.

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/snoriks/SecKing/releases)      [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)


### 🚀 INSTALLATION
-    Install the project dependencies using the command:  **pip install -r requirements.txt**
-  create **.env** file
- Create a cluster and connect it to **Visual Studio Code** using **MongoDB** on the page: [MongoDB](https://cloud.mongodb.com/)
- Create an account on **Hugging Face** and copy the token value to the page: [HuggingFace](https://huggingface.co/settings/tokens)

### 📜  .env
- **TOKEN**=your_discord_bot_token
- **HF_TOKEN**=your_huggingface_api_token
- **MONGO_URI**=your_mongodb_connection_string


#### 🤖 BOT COMMANDS
- **/warn** Apply a manual warning to a user with a mandatory reason. If they accumulate 3 warnings, a panel appears with buttons to ban, expel, or suspend the user.
 - Use: **/warn @user reason**
- **/warns** Displays a complete report of warns that a user has.
 - Use: **/warns @user**
- **/resetwarns** Allows you to reset or reduce a users warns by type (**manual, nsfw, violence**) and by a specific amount.
 - Use: **/resetwarns user: @user category: nsfw amount: 0**
- **/infoinsults** Displays the history of insults automatically detected by AI on a server user.
 - Use:   **/infoinsults @user**
- **/resetinsults** Completely erases the history of insults detected in a user.
 - Use: **/resetinsults @user**
- **/setlog** Establece el canal donde se enviarán los logs de moderación (**insultos, warns, imágenes, etc.**).
 - **/setlog channel: #channel-name**

---

### 👤 AUTHOR

Powered by 💻 and ☕ by  **Erick (Snoriks)**

- GitHub: [@snoriks](https://github.com/snoriks)
- Email: snorikv@gmail.com

