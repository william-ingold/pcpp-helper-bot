# pcpp-helper-bot
Helper bot for posting [PC Part Picker](https://pcpartpicker.com/) links as tables in Reddit and informing users
to anonymize their list URLs.

The bot will read through new submissions from [r/buildapc](https://www.reddit.com/r/buildapc) via [PRAW](https://praw.readthedocs.io/en/latest). Currently, only
submissions with the following flairs will be inspected: 
* Build Complete
* Build Upgrade
* Build Help
* Build Ready
* No flair

If a submission has PC Part Picker list URL, but either no table or a malformed one, the bot will post a reply
with a table with the list's components.

Additionally, if the bot detects an identifiable list URL, it will find the anonymous list URL and
inform the user to use it instead.

## Example
One example is below, additional ones are in the examples folder.

### Post
This is a test post. Here is an anonymous PCPP list url: https://pcpartpicker.com/list/ZqWwj2

### Reply:
Hello, I am the [PC Part Picker](https://pcpartpicker.com) Helper Bot!

Wah-oh! I found at least one instance of the following table issue(s) in your post: a missing table

To help out, I made this for you:

[PCPartPicker Part List](https://pcpartpicker.com/list/ZqWwj2)

Type|Item|Price
:----|:----|:----
 **CPU** | [AMD Ryzen 5 3600 3.6 GHz 6-Core Processor](https://pcpartpicker.com/product/9nm323/amd-ryzen-5-3600-36-thz-6-core-processor-100-100000031box) | $199.99 @ Best Buy
 **CPU Cooler** | [Cooler Master Hyper 212 EVO 82.9 CFM Sleeve Bearing CPU Cooler](https://pcpartpicker.com/product/hmtCmG/cooler-master-cpu-cooler-rr212e20pkr2) | $34.99 @ Amazon
 **Motherboard** | [MSI B450 TOMAHAWK MAX ATX AM4 Motherboard](https://pcpartpicker.com/product/jcYQzy/msi-b450-tomahawk-max-atx-am4-motherboard-b450-tomahawk-max) | $124.99 @ B&H Photo
 **Memory** | [Corsair Vengeance LPX 16 GB (2 x 8 GB) DDR4-3200 CL16 Memory](https://pcpartpicker.com/product/p6RFf7/corsair-memory-cmk16gx4m2b3200c16) | $78.98 @ Amazon
 **Storage** | [Seagate Barracuda Compute 2 TB 3.5" 7200RPM Internal Hard Drive](https://pcpartpicker.com/product/mwrYcf/seagate-barracuda-computer-2-tb-35-7200rpm-internal-hard-drive-st2000dm008) | $54.99 @ Newegg
 **Case** | [NZXT H510 ATX Mid Tower Case](https://pcpartpicker.com/product/6Cyqqs/nzxt-h510-atx-mid-tower-case-ca-h510b-w1) | $67.99 @ B&H Photo
 **Power Supply** | [Corsair RM (2019) 750 W 80+ Gold Certified Fully Modular ATX Power Supply](https://pcpartpicker.com/product/6Y66Mp/corsair-rm-2019-750-w-80-gold-certified-fully-modular-atx-power-supply-cp-9020195-na) | $134.99 @ Newegg
 *Prices include shipping, taxes, rebates, and discounts* | 
 | **Total** | **$696.92** | 
 Generated at 2021-01-20 10:12:59 EST-0500 |  |


PC Part Picker will create the table for you if you click on the Reddit logo at the top of your list.

---
Please don't reply directly to me, so that we can minimize spam! 

[You can PM me](https://www.reddit.com/message/compose/?to=pcpp-helper-bot) any concerns, issues, or suggestions!

My GitHub repository [can be found here](https://github.com/william-ingold/pcpp-helper-bot), if you'd like to take a gander. 

 ## Potential Ideas
 This could be linked up with [r/buildapcsales](https://www.reddit.com/r/buildapcsales) to determine if an item has recently gone on sale.
 The difficulty lies in tying the component and sale together. Either the name has to be similar
 or the linked vendor from PC Part Picker must be the same as the link from r/buildapcsales. Research
 and experimentation need to be done.
 
 Either read through comments for links as well, or await for a mention of the bot to post a list table
 in response to a comment.
 
 ## TODO
Work on getting the vendor names correct, since it's currently just parsing them from the affiliate URL.
