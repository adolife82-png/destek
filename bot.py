import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DESTEK_KANAL_ADI = "destek-aç"
YETKILI_ROL_ADI = "Support Team"  # Yetkili rol ismini buraya yaz

# ---------------------- TICKET KAPAT BUTONU ----------------------

class CloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket Kapat", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Ticket 5 saniye içinde kapatılıyor...", ephemeral=True)
        await interaction.channel.delete()

# ---------------------- KATEGORİ SEÇİM MENÜSÜ ----------------------

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Sipariş", description="Yeni sipariş vermek istiyorum", emoji="🛒"),
            discord.SelectOption(label="Destek", description="Bir sorunum var", emoji="🛠️"),
            discord.SelectOption(label="Proje İsteği", description="Özel proje talebi", emoji="⭐"),
            discord.SelectOption(label="Ücretsiz Proje", description="Ücretsiz proje bilgisi", emoji="🎁"),
            discord.SelectOption(label="Diğer", description="Diğer konular", emoji="❓")
        ]
        super().__init__(placeholder="Bir kategori seç...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        kategori = self.values[0]

        # Ticket zaten var mı kontrol
        mevcut = discord.utils.get(guild.text_channels, name=f"ticket-{user.id}")
        if mevcut:
            await interaction.response.send_message("Zaten açık bir ticketin var!", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        yetkili_rol = discord.utils.get(guild.roles, name=YETKILI_ROL_ADI)
        if yetkili_rol:
            overwrites[yetkili_rol] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            overwrites=overwrites,
            topic=f"{user} | {kategori}"
        )

        embed = discord.Embed(
            title="🎫 Atlas Project Destek",
            description=f"{user.mention} talebiniz oluşturuldu.\nKategori: **{kategori}**\nYetkililer en kısa sürede ilgilenecektir.",
            color=discord.Color.blue()
        )

        await channel.send(content=user.mention, embed=embed, view=CloseButton())
        await interaction.response.send_message(f"Ticket oluşturuldu: {channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# ---------------------- BOT HAZIR ----------------------

@bot.event
async def on_ready():
    print(f"{bot.user} aktif!")
    bot.add_view(TicketView())  # persistent view

# ---------------------- DESTEK MESAJINI GÖNDER ----------------------

@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
    embed = discord.Embed(
        title="📩 Atlas Project - Destek Merkezi",
        description=(
            "Aşağıdaki kategorilerden uygun olanı seçerek hemen ticket oluşturabilirsiniz.\n\n"
            "⚠️ Gereksiz ticket açmayınız."
        ),
        color=discord.Color.dark_blue()
    )

    await ctx.send(embed=embed, view=TicketView())

# ---------------------- TOKEN ----------------------

TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
