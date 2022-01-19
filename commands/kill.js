const { SlashCommandBuilder } = require(`@discordjs/builders`);

module.exports = {
    data: new SlashCommandBuilder().setName(`kill`).setDescription(`Completely shut down the bot.`),
    async execute(interaction) {
        await interaction.reply({ content: `bruh, ok fine. shutting down. (kys)`, empheral: true });
    },
};