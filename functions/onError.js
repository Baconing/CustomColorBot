const { MessageEmbed } = require(`discord.js`);

const customErrors = [
    { "name": `MissingPermissions`, "message": `You do not have the required permissions to perform this action.` },
    { "name": `MissingArgument`, "message": `You are missing a required argument.` },
];
const blockedErrors = [];

module.exports = {
    name: `onError`,
    execute(error, interaction) {
        console.log(error);
        const embed = new MessageEmbed()
            .setColor(`#ff0000`)
            .setTitle(`An error has occured!`)
            .setTimestamp();

        if (error.message in blockedErrors) return;

        if (error.message in customErrors) {
            embed.addField(`Error`, customErrors[error.message]);
            embed.addField(`Support`, `none yet HAHAHHAHAH L BOZO + RADIO`);
        } else {
            embed.addField(`Error`, error);
            embed.addField(`Support`, `none yet HAHAHHAHAH L BOZO + RADIO`);
        }

        interaction.reply({ embeds: [embed], ephmeral: true });
    },
};