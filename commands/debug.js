const { SlashCommandBuilder } = require(`@discordjs/builders`);
const { MessageEmbed } = require(`discord.js`);

module.exports = {
    data: new SlashCommandBuilder().setName(`debug`).setDescription(`Status of the bot for owner(s).`),
    async execute(interaction) {
        const embed = new MessageEmbed()
            .setColor(`#0099ff`)
            .setTitle(`Status`)
            .setDescription(`Status information.\n\n:green_circle: - Working as intended.\n:yellow_circle: - Lagging, not fully working as intended but main features still work. (Maybe restart?)\n:red_circle: - Fatal errors, unusable, crashed.`)
            .addField({ name: `Uptime`, value: `${Math.floor(interaction.client.uptime / 1000)} seconds.` })
            .setTimestamp();

        await interaction.reply({ embeds: [embed], empheral: true });
    },
};