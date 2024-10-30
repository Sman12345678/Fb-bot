const login = require("facebook-chat-api");
require("dotenv").config();
const port = process.env.PORT || 3000;

const email = process.env.FB_EMAIL;
const password = process.env.FB_PASSWORD;
const prefix = process.env.PREFIX;

// Login to Facebook
login({email: email, password: password}, (err, api) => {
    if (err) return console.error(err);

    console.log("Facebook bot is now listening for messages...");

    // Listen for incoming messages
    api.listen((err, message) => {
        if (err) console.error(err);

        // Check if the message starts with the defined prefix
        if (message.body && message.body.startsWith(prefix)) {
            const commandName = message.body.slice(prefix.length).split(" ")[0];

            if (commandName === "hello") {
                api.sendMessage("Hello! This is an automated response.", message.threadID);
            }
            // Add other command checks here based on commandName
        }
    });
});
