const { REST } = require(`@discordjs/rest`);
const { Routes } = require(`discord-api-types/v9`);
const fs = require(`fs`);

module.export = {
    name: `syncCommands`,
    description: `Sync commands with Discord`,
    execute(token, clientID, debugGuild = null, commandsFolder, type) {
        const commands = [];
        const commandFiles = fs.readdirSync(commandsFolder).filter(file => file.endsWith(`.js`));
        for (const file of commandFiles) {
            const command = require(`${commandsFolder}/${file}`);
            commands.push(command.data.toJSON());
        }

        const rest = new REST({ version: `9` }).setToken(token);

        if (type == `dev`) {
            
            rest.put(Routes.applicationGuildCommands(clientID, debugGuild), { body: commands })
                .then(() => console.log(`Synced guild commands.`))
                .catch(console.error);
        } else {
            rest.put(Routes.applicationCommands(clientID), { body: commands })
                .then(() => console.log(`Synced commands with Discord. Expect to take an hour or so to fully sync.`))
                .catch(console.error);
        }
    },
};