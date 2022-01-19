require(`dotenv`).config();
const type = process.argv.slice(2)[0];

const { Client, Collection, Intents } = require(`discord.js`);
const fs = require(`fs`);

const onError = require(`./functions/onError.js`);
const syncCommands = require(`./functions/syncCommands.js`);

const testingIntents = [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MEMBERS, Intents.FLAGS.GUILD_BANS, Intents.FLAGS.GUILD_EMOJIS_AND_STICKERS, Intents.FLAGS.GUILD_INTEGRATIONS, Intents.FLAGS.GUILD_WEBHOOKS, Intents.FLAGS.GUILD_INVITES, Intents.FLAGS.GUILD_VOICE_STATES, Intents.FLAGS.GUILD_PRESENCES, Intents.FLAGS.GUILD_MESSAGES, Intents.FLAGS.GUILD_MESSAGE_REACTIONS, Intents.FLAGS.GUILD_MESSAGE_TYPING, Intents.FLAGS.DIRECT_MESSAGES, Intents.FLAGS.DIRECT_MESSAGE_REACTIONS, Intents.FLAGS.DIRECT_MESSAGE_TYPING, Intents.FLAGS.GUILD_SCHEDULED_EVENTS];
const normalIntents = [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MEMBERS];

// const client = new Client({ intents: normalIntents });
const client = new Client ({ intents: testingIntents });

const token = process.env.DEVTOKEN;
const clientId = process.env.DEVCLIENTID;
const debugGuild = process.env.DEBUGGUILD;

/*
const token = process.env.TOKEN;
const clientId = process.env.CLIENTID;
*/

client.commands = new Collection();
const commandFiles = fs.readdirSync(`./commands`).filter(file => file.endsWith(`.js`));

syncCommands.execute(client, token, clientId, debugGuild, type);

for (const file of commandFiles) {
    const command = require(`./commands/${file}`);
    client.commands.set(command.name, command);
}

const eventFiles = fs.readdirSync(`./events`).filter(file => file.endsWith(`.js`));
for (const file of eventFiles) {
    const event = require(`./events/${file}`);
    if (event.once) {
        client.once(event.name, (...args) => event.execute(client, ...args));
    } else {
        client.on(event.name, (...args) => event.execute(client, ...args));
    }
}

client.on(`interactionCreate`, async interactrion => {
    if (!interactrion.isCommand()) return;
    const command = client.commands.get(interactrion.commandName);

    if (!command) return;

    try {
        await command.execute(interaction);
    } catch (error) {
        onError(error, interaction);
    }
});

client.login(token);