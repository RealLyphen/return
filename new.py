from telethon import TelegramClient, events, Button
from telethon.errors import UserAdminInvalidError, ChatAdminRequiredError
from telethon.tl.functions.messages import ExportChatInviteRequest
import os
import asyncio
import json
import traceback
import hashlib
import random
import re
from datetime import datetime, timedelta
from oxapay_api.SyncOxaPay import SyncOxaPay  # CORRECTED IMPORT

# Bot credentials
API_ID = '24839357'
API_HASH = '4c7ac3d774fd95bf81d3924cf012978b'
BOT_TOKEN = '7693026027:AAGZClqTAP5BxMXou_kSqabIswyAJPvwCi0'

# OxaPay Configuration
OXAPAY_MERCHANT_KEY = 'NBOZLB-6FE14E-LNG1C0-XPTDVN'  # Your actual merchant key

# Initialize OxaPay client
try:
    oxapay = SyncOxaPay(merchant_api_key=OXAPAY_MERCHANT_KEY)
    print("✅ OxaPay initialized successfully")
except Exception as e:
    print(f"⚠️ OxaPay initialization error: {e}")
    oxapay = None

# Admin and group settings
ADMIN_IDS = [5917165243, 7207727106, 5640641472]  # Support multiple admins
GROUP_ID = -1002712666768
VOUCHES_CHANNEL_ID = -1002919289402
ORDERS_CHANNEL_ID = -1002919289402
PAYMENT_NOTIFICATION_CHANNEL = -1002919289402  # Channel for payment notifications
LOGS_CHANNEL_ID = -1003288395320  # All logs channel

# Invite Channel IDs
FREE_SAUCE_CHANNEL_ID = -1002919289402
BOXING_SERVICE_CHANNEL_ID = -1002919289402
CASHBACK_SERVICE_CHANNEL_ID = -1002919289402
CHAT_CHANNEL_ID = -1002919289402
TEACHING_ACADEMY_CHANNEL_ID = -1002919289402

# Initialize bot
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# States
broadcast_state = {}
order_states = {}
admin_remark_state = {}
ticket_states = {}
raffle_creation_state = {}
deposit_states = {}
boxing_service_states = {}
admin_complete_order_states = {}
captcha_states = {}  # Stores captcha data: {user_id: {'answer': int, 'failed_at': timestamp, 'ref_code': str}}
verified_users = {}  # Users who have passed captcha: {user_id: verification_timestamp}
admin_resources_state = {}  # Stores state for updating resources link
admin_form_state = {}  # Stores state for updating form link
admin_service_state = {}  # Stores state for adding custom services
admin_reseller_state = {}  # Stores state for setting reseller pricing
admin_method_state = {}  # Stores state for adding/editing methods
method_purchase_state = {}  # Stores state for purchasing methods

# Files
user_list_file = 'users.txt'
user_data_file = 'user_data.json'
orders_file = 'orders.json'
tickets_file = 'tickets.json'
raffles_file = 'raffles.json'
service_orders_file = 'service_orders.json'
payments_file = 'payments.json'
resources_file = 'resources.json'
form_file = 'form.json'
custom_services_file = 'custom_services.json'
reseller_pricing_file = 'reseller_pricing.json'
methods_file = 'methods.json'
method_purchases_file = 'method_purchases.json'

# Create directories
os.makedirs('transcripts', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

# Store Database - Organized by Region and Category
STORES = {
    "USA": {
        "name": "🇺🇸 United States",
        "flag": "🇺🇸",
        "categories": {
    "electronics": {
        "name": "💻 Electronics",
        "stores": {
                    "apple_usa": {
                        "name": "🍎 Apple",
                        "fee": "18%",
                        "limit": "$5000",
                        "items": "1 item",
                        "timeframe": "1-2 days",
                        "region": "USA/CA/DE",
                        "success_rate": "100%",
                        "description": "🔄 Reship available\n⚡ Triple dip available - aged apple ID needed",
                        "notes": "Contact @return"
            },
            "bestbuy": {
                "name": "🔵 Best Buy",
                        "fee": "20%",
                        "limit": "$7000",
                        "items": "5 items",
                        "timeframe": "2 days",
                        "region": "USA",
                        "success_rate": "100%",
                        "description": "Fresh accounts work\n✅ Shipped by BestBuy only\n❌ No pickup, same day delivery, freight, or scheduled delivery\n🔄 Reship works if order goes through",
                        "notes": ""
                    },
                    "samsung": {
                        "name": "📱 Samsung",
                        "fee": "18%",
                        "limit": "$3000",
                        "items": "2 items max (1 is highest SR)",
                        "timeframe": "1 day",
                        "region": "USA",
                        "success_rate": "100%",
                        "description": "Contact @return for more info",
                        "notes": ""
                    },
                    "steamdeck_ww": {
                        "name": "🎮 Steamdeck",
                        "fee": "18%",
                        "limit": "$3500",
                        "items": "2 items (must be same)",
                        "timeframe": "3 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "⚡ Exclusive new method\n🔄 Repeatable to same address\n💎 Double dips working\n✅ Fresh accounts working",
                        "notes": ""
                    },
                    "playstation_direct": {
                        "name": "🎮 PlayStation Direct",
                        "fee": "18%",
                        "limit": "$1000",
                        "items": "1 item",
                        "timeframe": "3-5 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "⚡ Exclusive method\n🔄 Repeatable to same address\n✅ Fresh accounts working\n⏱️ Extremely fast refund\n🔒 No rebills (safe procedure)\n❌ No reships or pickups",
                        "notes": ""
                    },
                    "walmart": {
                        "name": "🛒 Walmart",
                        "fee": "18%",
                        "limit": "$4000",
                        "items": "2 items",
                        "timeframe": "0-24 hours",
                        "region": "USA",
                        "success_rate": "100%",
                        "description": "⚡ SAFEST HIGHEST SR METHOD\n💻 Any electronic items work\n✅ Fresh accounts works\n⚠️ YOU MUST CONTACT BEFORE PLACING ORDER\n❌ No reships, same-day delivery, or previous refunds on same account/address",
                        "notes": ""
                    },
                    "staples": {
                        "name": "📎 Staples",
                        "fee": "18%",
                        "limit": "$3000",
                        "items": "1 item",
                        "timeframe": "0-24 hours",
                        "region": "USA",
                        "success_rate": "100%",
                        "description": "⚡ INSTANT REFUNDS\n🔥 HOT STORE - PRIVATE METHOD\n✅ Fresh accounts working\n🔄 Repeatable to same address\n❌ No reships or pickups",
                        "notes": ""
                    },
                    "nikon_usa_ca": {
                        "name": "📷 Nikon",
                        "fee": "18%",
                        "limit": "$8000",
                        "items": "3 items",
                        "timeframe": "7-14 days",
                        "region": "USA/CA",
                        "success_rate": "100%",
                        "description": "⚡ SAFEST HIGHEST SR METHOD\n📸 Any items working\n🔄 Refunds not replacements\n✅ Fresh accounts working\n📦 Reships allowed",
                        "notes": ""
                    },
                    "canon_usa": {
                        "name": "📷 Canon",
                        "fee": "18%",
                        "limit": "$8000",
                        "items": "3 items",
                        "timeframe": "7-14 days",
                        "region": "USA/EU/UK",
                        "success_rate": "100%",
                        "description": "⚡ FASTEST AND HIGHEST SR METHOD\n⏱️ Most orders finished within 1 week\n✅ Fresh accounts working\n🔄 REFUNDS only. No replacements\n📦 Reships working",
                        "notes": ""
                    },
                    "dyson_usa": {
                        "name": "💨 Dyson",
                        "fee": "18%",
                        "limit": "$2500",
                        "items": "3 items",
                        "timeframe": "0-24 hours",
                        "region": "USA",
                        "success_rate": "100%",
                        "description": "⚡ INSTANT REPLACEMENT only\n✅ Fresh accounts okay\n❌ No freight, pickup, or same day delivery",
                        "notes": ""
                    },
                    "lowes": {
                        "name": "🔨 Lowes",
                        "fee": "18%",
                        "limit": "$4000",
                        "items": "1 item",
                        "timeframe": "3 days",
                        "region": "USA/CA",
                        "success_rate": "100%",
                        "description": "🔥 HOT STORE - PRIVATE METHOD\n✅ Must be sold by LOWES\n✅ Fresh accounts working\n🔄 Repeatable to same address\n💡 Honda generators and Dyson vacuums great resell\n❌ No reships or pickups",
                        "notes": ""
                    },
                    "nectar_sleep": {
                        "name": "🛏️ Nectar Sleep",
                        "fee": "18%",
                        "limit": "$5000",
                        "items": "2 items",
                        "timeframe": "0-3 days",
                        "region": "USA/CA",
                        "success_rate": "100%",
                        "description": "⚡ FASTEST MOST RELIABLE METHOD\n✅ Fresh accounts working\n📦 Any items working\n🔄 Repeatable to same address",
                        "notes": ""
                    }
                }
            },
            "retail": {
                "name": "🏬 Retail & Wholesale",
                "stores": {
                    "amazon_usa": {
                        "name": "📦 Amazon",
                        "fee": "18%",
                        "limit": "£10000",
                        "items": "10 items",
                        "timeframe": "Varies",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "🌍 Worldwide coverage\n✅ Trusted and reliable",
                        "notes": ""
                    },
                    "target": {
                        "name": "🎯 Target",
                        "fee": "18%",
                        "limit": "$10000",
                        "items": "5 items",
                        "timeframe": "14-21 days",
                        "region": "USA",
                        "success_rate": "100%",
                        "description": "⚡ SAFEST HIGHEST SR METHOD\n🔄 Repeatable to same address\n📦 Items must be returnable to Target.com\n✅ Any seller works, fresh accounts works\n❌ No apple devices, pickups, or reships",
                        "notes": ""
                    },
                    "samsclub": {
                        "name": "🏪 Sam's Club",
                        "fee": "18%",
                        "limit": "$10000",
                        "items": "2 items (must be same)",
                        "timeframe": "0-24 hours",
                        "region": "USA",
                        "success_rate": "100%",
                        "description": "⚡ INSTANT HIGHEST SR METHOD\n💎 Triple dips doable\n🍎 Any items working (including Apple)\n🔄 Replacements not refunds\n✅ Fresh accounts working (buy membership before placing order)\n❌ No reships allowed",
                        "notes": ""
            }
        }
    },
    "fashion": {
        "name": "👗 Fashion & Apparel",
        "stores": {
                    "ralph_lauren_ww": {
                        "name": "👔 Ralph Lauren",
                        "fee": "18%",
                        "limit": "$10000",
                        "items": "20 items",
                        "timeframe": "14 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "🔥 HOTTT STORE\n✅ Fresh accounts working\n📦 Standard shipping only\n🌍 Working smooth WORLDWIDE",
                        "notes": ""
                    },
                    "skims": {
                        "name": "👙 SKIMS",
                        "fee": "18%",
                        "limit": "£2500",
                        "items": "25 items",
                        "timeframe": "10-14 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "Popular fashion brand",
                        "notes": ""
                    }
                }
            },
            "luxury": {
                "name": "💎 Luxury & Designer",
                "stores": {
                    "bloomingdales": {
                        "name": "🌸 Bloomingdales",
                        "fee": "18%",
                        "limit": "$10000",
                        "items": "15-20 items",
                        "timeframe": "14-21 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "⚡ HIGHEST SR METHOD\n❌ No jewellery\n🔄 Repeatable to same address\n✅ Fresh accounts works\n📦 Reships allowed",
                        "notes": ""
                    },
                    "burberry": {
                        "name": "🧥 Burberry",
                        "fee": "18%",
                        "limit": "£2000",
                        "items": "1 item",
                        "timeframe": "14-30 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "Premium luxury brand",
                        "notes": "Contact @return"
                    }
                }
            },
            "home": {
                "name": "🏡 Home & Furniture",
        "stores": {
                    "wayfair_ww": {
                        "name": "🛋️ Wayfair",
                        "fee": "18%",
                        "limit": "$10000",
                        "items": "7 items",
                        "timeframe": "INSTANT",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "⚡ UNIQUE PRIVATE METHOD\n⏱️ INSTANT timeframe\n✅ Fresh accounts working\n📦 Any items working\n🌍 Working smooth WORLDWIDE\n🔄 Repeatable to same address",
                        "notes": ""
                    }
                }
            },
            "financial": {
                "name": "💰 Financial Services",
                "stores": {
                    "paypal_claims": {
                        "name": "💳 PayPal Claims",
                        "fee": "18%",
                        "limit": "No limit",
                        "items": "Any transaction",
                        "timeframe": "14-30 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "High",
                        "description": "Any transaction can be claimed\n❌ No instructions needed - place order as normal then message @return to begin refund process",
                        "notes": ""
                    },
                    "bank_disputes": {
                        "name": "🏦 Bank Disputes",
                        "fee": "18%",
                        "limit": "No limit",
                        "items": "Any transaction",
                        "timeframe": "21-30 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "High",
                        "description": "Any purchases from any store can be refunded\n🔄 Repeatable for multiple transactions\n🌍 Works with ANY BANK",
                        "notes": ""
                    }
                }
            }
        }
    },
    "UK": {
        "name": "🇬🇧 United Kingdom",
        "flag": "🇬🇧",
        "categories": {
            "electronics": {
                "name": "💻 Electronics",
                "stores": {
                    "lenovo": {
                        "name": "💻 Lenovo",
                        "fee": "18%",
                        "limit": "£5000",
                        "items": "1 item",
                        "timeframe": "INSTANT",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "⚡ INSTANT REPLACEMENT\n🌍 Worldwide coverage",
                        "notes": ""
                    },
                    "hp_uk": {
                        "name": "🖥️ HP",
                        "fee": "18%",
                        "limit": "£5000",
                        "items": "2 items",
                        "timeframe": "7-14 days",
                        "region": "UK/EU",
                        "success_rate": "100%",
                        "description": "⚡ SAFEST HIGHEST SR METHOD\n🔄 Repeatable to same address\n📦 Residential reship working\n💎 Double dip possible",
                        "notes": ""
                    },
                    "canon_uk": {
                        "name": "📷 Canon",
                        "fee": "18%",
                        "limit": "$8000",
                        "items": "3 items",
                        "timeframe": "7-14 days",
                        "region": "USA/EU/UK",
                        "success_rate": "100%",
                        "description": "⚡ FASTEST AND HIGHEST SR METHOD\n⏱️ Most orders finished within 1 week\n✅ Fresh accounts working\n🔄 REFUNDS only. No replacements\n📦 Reships working",
                        "notes": ""
                    },
                    "steelseries": {
                        "name": "🎮 SteelSeries",
                        "fee": "18%",
                        "limit": "£1500",
                        "items": "3 items",
                        "timeframe": "14 days",
                        "region": "UK",
                        "success_rate": "100%",
                        "description": "🔥 HOT UK STORE - GREAT RESELL\n✅ Fresh accounts working\n📦 Any item working\n❌ No reships or pickups",
                        "notes": ""
                    }
                }
            },
            "home": {
                "name": "🏡 Home & Furniture",
                "stores": {
                    "ikea": {
                        "name": "🛋️ IKEA",
                        "fee": "18%",
                        "limit": "£1200",
                        "items": "1 item",
                        "timeframe": "3 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "❌ No reship, no pickup",
                        "notes": ""
                    },
                    "emma_sleep_ww": {
                        "name": "🛏️ Emma Sleep",
                        "fee": "18%",
                        "limit": "$5000",
                        "items": "2 items",
                        "timeframe": "3-14 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "🔥 HOT STORE - PRIVATE METHOD\n✅ Fresh accounts working\n🔄 Repeatable to same address\n❌ No reships or pickups",
                        "notes": ""
                    },
                    "herman_miller_ww": {
                        "name": "🪑 Herman Miller",
                        "fee": "18%",
                        "limit": "$5000",
                        "items": "1 item",
                        "timeframe": "14 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "🔥 HOT STORE - PRIVATE METHOD\n✅ Fresh accounts working\n🔄 Repeatable to same address\n❌ No reships or pickups",
                        "notes": ""
            }
        }
    },
    "retail": {
        "name": "🏬 Retail & Wholesale",
        "stores": {
                    "amazon_uk": {
                        "name": "📦 Amazon",
                        "fee": "18%",
                        "limit": "£10000",
                        "items": "10 items",
                        "timeframe": "Varies",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "🌍 Worldwide coverage",
                        "notes": ""
                    }
                }
            },
            "tech": {
                "name": "🔧 Tech & Gadgets",
                "stores": {
                    "oneplus": {
                        "name": "📱 OnePlus",
                        "fee": "18%",
                        "limit": "£2000",
                        "items": "5 items",
                        "timeframe": "14 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "Premium smartphone brand",
                        "notes": ""
                    },
                    "meta": {
                        "name": "🥽 Meta",
                        "fee": "18%",
                        "limit": "£3000",
                        "items": "3 items (must be same)",
                        "timeframe": "7-10 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "VR headsets and accessories",
                        "notes": ""
                    }
                }
            },
            "other": {
                "name": "🌐 Other Services",
                "stores": {
                    "ring": {
                        "name": "🔔 Ring",
                        "fee": "18%",
                        "limit": "No limit",
                        "items": "Unlimited",
                        "timeframe": "7 days max (often instant)",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "❌ No order limit - Unlimited price and items!",
                        "notes": ""
                    },
                    "ebay_instant": {
                        "name": "🛍️ eBay Instant",
                        "fee": "18%",
                        "limit": "$£€8000",
                        "items": "1 item",
                        "timeframe": "0-24 hours",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "⚡ NEW INSTANT METHOD\n📱 Electronics only\n✅ Any seller, fresh accounts work\n❌ No freight, no pickup",
                        "notes": ""
                    }
                }
            }
        }
    },
    "EU": {
        "name": "🇪🇺 European Union",
        "flag": "🇪🇺",
        "categories": {
            "electronics": {
                "name": "💻 Electronics",
                "stores": {
                    "canon_eu": {
                        "name": "📷 Canon",
                        "fee": "18%",
                        "limit": "$8000",
                        "items": "3 items",
                        "timeframe": "7-14 days",
                        "region": "USA/EU/UK",
                        "success_rate": "100%",
                        "description": "⚡ FASTEST AND HIGHEST SR METHOD\n⏱️ Most orders finished within 1 week\n✅ Fresh accounts working\n🔄 REFUNDS only. No replacements\n📦 Reships working",
                        "notes": ""
                    },
                    "hp_eu": {
                        "name": "🖥️ HP",
                        "fee": "18%",
                        "limit": "£5000",
                        "items": "2 items",
                        "timeframe": "7-14 days",
                        "region": "UK/EU",
                        "success_rate": "100%",
                        "description": "⚡ SAFEST HIGHEST SR METHOD\n🔄 Repeatable to same address\n📦 Residential reship working\n💎 Double dip possible",
                        "notes": ""
                    },
                    "bambulabs": {
                        "name": "🖨️ BambuLabs",
                        "fee": "18%",
                        "limit": "$5000",
                        "items": "1 item",
                        "timeframe": "14-21 days",
                        "region": "EU/GB",
                        "success_rate": "100%",
                        "description": "🔥 HOT STORE\n✅ Fresh accounts working\n🔄 Repeatable to same address\n❌ No freight, reships, or pickups",
                        "notes": ""
                    }
                }
            },
            "tech": {
                "name": "🔧 Tech & Software",
                "stores": {
                    "microsoft_ww": {
                        "name": "🪟 Microsoft",
                        "fee": "18%",
                        "limit": "$5000",
                        "items": "3 items",
                        "timeframe": "7-14 days",
                        "region": "Worldwide 🌐",
                        "success_rate": "100%",
                        "description": "⚡ FASTEST AND HIGHEST SR METHOD\n⏱️ Most orders finished within 1 week\n✅ Fresh accounts working\n🌍 Working worldwide\n❌ No reships or pickups",
                        "notes": ""
                    }
                }
            }
        }
    },
    "CA": {
        "name": "🇨🇦 Canada",
        "flag": "🇨🇦",
        "categories": {
            "electronics": {
                "name": "💻 Electronics",
                "stores": {
                    "apple_ca": {
                        "name": "🍎 Apple",
                        "fee": "18%",
                        "limit": "$5000",
                        "items": "1 item",
                        "timeframe": "1-2 days",
                        "region": "USA/CA/DE",
                        "success_rate": "100%",
                        "description": "🔄 Reship available\n⚡ Triple dip available - aged apple ID needed",
                        "notes": "Contact @return"
                    },
                    "nikon_ca": {
                        "name": "📷 Nikon",
                        "fee": "18%",
                        "limit": "$8000",
                        "items": "3 items",
                        "timeframe": "7-14 days",
                        "region": "USA/CA",
                        "success_rate": "100%",
                        "description": "⚡ SAFEST HIGHEST SR METHOD\n📸 Any items working\n🔄 Refunds not replacements\n✅ Fresh accounts working\n📦 Reships allowed",
                        "notes": ""
                    },
                    "shark_ninja": {
                        "name": "🦈 Shark Ninja",
                        "fee": "18%",
                        "limit": "$2000 CAD",
                        "items": "2 items",
                        "timeframe": "3 days",
                        "region": "CA",
                        "success_rate": "100%",
                        "description": "🔥 HOT STORE - PRIVATE METHOD\n✅ Fresh accounts working\n🔄 Repeatable to same address\n❌ No reships or pickups",
                        "notes": ""
                    }
                }
            },
            "home": {
                "name": "🏡 Home & Improvement",
                "stores": {
                    "lowes_ca": {
                        "name": "🔨 Lowes",
                        "fee": "18%",
                        "limit": "$4000",
                        "items": "1 item",
                        "timeframe": "3 days",
                        "region": "USA/CA",
                        "success_rate": "100%",
                        "description": "🔥 HOT STORE - PRIVATE METHOD\n✅ Must be sold by LOWES\n✅ Fresh accounts working\n🔄 Repeatable to same address\n💡 Honda generators and Dyson vacuums great resell\n❌ No reships or pickups",
                        "notes": ""
                    },
                    "nectar_sleep_ca": {
                        "name": "🛏️ Nectar Sleep",
                        "fee": "18%",
                        "limit": "$5000",
                        "items": "2 items",
                        "timeframe": "0-3 days",
                        "region": "USA/CA",
                        "success_rate": "100%",
                        "description": "⚡ FASTEST MOST RELIABLE METHOD\n✅ Fresh accounts working\n📦 Any items working\n🔄 Repeatable to same address",
                        "notes": ""
                    }
                }
            }
        }
    }
}

# Boxing Service Prices
BOXING_SERVICES = {
    "ftid": {
        "name": "📦 FTID - UPS/USPS/FEDEX",
        "price": 18,
        "requires_form": True,
        "note": "📄 <i>PDF file is recommended for best results</i>"
    },
    "rts_dmg": {
        "name": "📮 RTS + DMG Left with Sender",
        "price": 40,
        "requires_tracking": True,
        "note": "📦 <i>Enter Tracking Number - Only delivered trackings!</i>"
    },
    "ups_lit": {
        "name": "🎨 UPS LIT",
        "price": 27,
        "requires_form": True,
        "note": "📄 <i>PDF file is recommended for best results</i>"
    }
}

# Helper functions
def log_error(error_msg, exc_info=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_msg = f"[{timestamp}] {error_msg}"
    
    if exc_info:
        full_msg += f"\n{traceback.format_exc()}"
    
    print(f"\n{'='*60}")
    print(f"❌ ERROR: {full_msg}")
    print(f"{'='*60}\n")
    
    with open('logs/errors.log', 'a', encoding='utf-8') as f:
        f.write(full_msg + "\n\n")
    
    # Also send to logs channel
    asyncio.create_task(send_log_to_channel("❌ ERROR", error_msg, exc_info=exc_info))

async def send_log_to_channel(log_type, message, user_id=None, username=None, exc_info=None):
    """Send logs to the logs channel with clickable profile links"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_msg = f"<b>{log_type}</b>\n"
        log_msg += f"<b>⏰ Time:</b> {timestamp}\n"
        
        if user_id:
            log_msg += f"<b>👤 User:</b> <a href='tg://user?id={user_id}'>{username or 'User'}</a> (ID: {user_id})\n"
        
        log_msg += f"<b>📝 Message:</b> {message}\n"
        
        if exc_info:
            log_msg += f"\n<code>{traceback.format_exc()}</code>"
        
        await bot.send_message(LOGS_CHANNEL_ID, log_msg, parse_mode='html')
    except Exception as e:
        print(f"Failed to send log to channel: {e}")

def load_json(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        log_error(f"Failed to load {filename}", e)
    return {}

def save_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log_error(f"Failed to save {filename}", e)

def is_admin(user_id):
    """Check if user is an admin"""
    return user_id in ADMIN_IDS

async def notify_admins(message, buttons=None, parse_mode='html', file=None):
    """Send a message to all admins"""
    for admin_id in ADMIN_IDS:
        try:
            if file:
                await bot.send_file(admin_id, file, caption=message, buttons=buttons, parse_mode=parse_mode)
            else:
                await bot.send_message(admin_id, message, buttons=buttons, parse_mode=parse_mode)
        except Exception as e:
            log_error(f"Failed to notify admin {admin_id}", e)

def get_resources_link():
    """Get current resources link"""
    data = load_json(resources_file)
    return data.get('link', 'https://example.com/resources')  # Default link

def set_resources_link(link):
    """Set resources link"""
    data = {'link': link}
    save_json(resources_file, data)

def get_form_link():
    """Get current form link"""
    data = load_json(form_file)
    return data.get('link', 'https://forms.gle/example')  # Default link

def set_form_link(link):
    """Set form link"""
    data = {'link': link}
    save_json(form_file, data)

def get_custom_services():
    """Get all custom services"""
    return load_json(custom_services_file)

def add_custom_service(service_id, name, description, price):
    """Add a new custom service"""
    services = get_custom_services()
    services[service_id] = {
        'name': name,
        'description': description,
        'price': price,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_json(custom_services_file, services)
    return True

def delete_custom_service(service_id):
    """Delete a custom service"""
    services = get_custom_services()
    if service_id in services:
        del services[service_id]
        save_json(custom_services_file, services)
        return True
    return False

def get_reseller_pricing():
    """Get all reseller pricing"""
    return load_json(reseller_pricing_file)

def get_user_price(user_id, service_name, default_price):
    """Get price for user (reseller price if set, otherwise default)"""
    pricing = get_reseller_pricing()
    user_pricing = pricing.get(str(user_id), {})
    return user_pricing.get(service_name, default_price)

def set_reseller_pricing(user_id, service_name, price):
    """Set custom pricing for a reseller"""
    pricing = get_reseller_pricing()
    if str(user_id) not in pricing:
        pricing[str(user_id)] = {}
    pricing[str(user_id)][service_name] = price
    save_json(reseller_pricing_file, pricing)
    return True

def remove_reseller_pricing(user_id, service_name=None):
    """Remove reseller pricing (specific service or all)"""
    pricing = get_reseller_pricing()
    if str(user_id) in pricing:
        if service_name:
            if service_name in pricing[str(user_id)]:
                del pricing[str(user_id)][service_name]
        else:
            del pricing[str(user_id)]
        save_json(reseller_pricing_file, pricing)
        return True
    return False

# Method Store Functions
def get_all_methods():
    """Get all methods"""
    return load_json(methods_file)

def get_method(method_id):
    """Get specific method"""
    methods = get_all_methods()
    return methods.get(str(method_id))

def add_method(method_data):
    """Add a new method"""
    methods = get_all_methods()
    method_id = str(len(methods) + 1)
    methods[method_id] = {
        'id': method_id,
        'name': method_data['name'],
        'price': method_data['price'],
        'description': method_data.get('description', ''),
        'tags': method_data.get('tags', []),
        'region': method_data.get('region', 'Worldwide'),
        'pdf_file': method_data.get('pdf_file'),
        'image_file': method_data.get('image_file'),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_json(methods_file, methods)
    return method_id

def get_methods_by_region(region):
    """Get all methods for a specific region"""
    all_methods = get_all_methods()
    return {mid: m for mid, m in all_methods.items() if m.get('region', 'Worldwide') == region}

def update_method(method_id, updates):
    """Update method details"""
    methods = get_all_methods()
    if str(method_id) in methods:
        methods[str(method_id)].update(updates)
        save_json(methods_file, methods)
        return True
    return False

def delete_method(method_id):
    """Delete a method"""
    methods = get_all_methods()
    if str(method_id) in methods:
        del methods[str(method_id)]
        save_json(methods_file, methods)
        return True
    return False

def get_user_methods(user_id):
    """Get methods purchased by user"""
    purchases = load_json(method_purchases_file)
    return purchases.get(str(user_id), [])

def add_method_purchase(user_id, method_id):
    """Record method purchase"""
    purchases = load_json(method_purchases_file)
    if str(user_id) not in purchases:
        purchases[str(user_id)] = []
    
    purchase = {
        'method_id': method_id,
        'purchased_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    purchases[str(user_id)].append(purchase)
    save_json(method_purchases_file, purchases)
    return True

def has_purchased_method(user_id, method_id):
    """Check if user has purchased a method"""
    user_methods = get_user_methods(user_id)
    return any(m['method_id'] == str(method_id) for m in user_methods)

def get_all_users():
    """Get list of all user IDs"""
    try:
        if os.path.exists(user_list_file):
            with open(user_list_file, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        return []
    except:
        return []

def save_user(user_id):
    try:
        users = set()
        if os.path.exists(user_list_file):
            with open(user_list_file, 'r') as f:
                users = set(f.read().splitlines())
        users.add(str(user_id))
        with open(user_list_file, 'w') as f:
            f.write('\n'.join(users))
    except Exception as e:
        log_error(f"Failed to save user {user_id}", e)

def get_all_users():
    try:
        if os.path.exists(user_list_file):
            with open(user_list_file, 'r') as f:
                return [int(uid) for uid in f.read().splitlines() if uid.strip()]
    except Exception as e:
        log_error("Failed to get users", e)
    return []

def generate_referral_code(user_id):
    """Generate unique referral code for user"""
    hash_obj = hashlib.md5(str(user_id).encode())
    return hash_obj.hexdigest()[:8].upper()

def get_user_data(user_id):
    data = load_json(user_data_file)
    if str(user_id) not in data:
        data[str(user_id)] = {
            'name': '',
            'join_date': datetime.now().strftime('%Y-%m-%d'),
            'orders': [],
            'service_orders': [],
            'referral_code': generate_referral_code(user_id),
            'referred_by': None,
            'referrals': [],
            'wallet_balance': 0.0,
            'payment_history': []
        }
        save_json(user_data_file, data)
    
    # Ensure wallet fields exist for existing users
    if 'wallet_balance' not in data[str(user_id)]:
        data[str(user_id)]['wallet_balance'] = 0.0
    if 'payment_history' not in data[str(user_id)]:
        data[str(user_id)]['payment_history'] = []
    if 'service_orders' not in data[str(user_id)]:
        data[str(user_id)]['service_orders'] = []
    
    return data[str(user_id)]

def update_user_data(user_id, updates):
    data = load_json(user_data_file)
    if str(user_id) not in data:
        data[str(user_id)] = {
            'name': '',
            'join_date': datetime.now().strftime('%Y-%m-%d'),
            'orders': [],
            'service_orders': [],
            'referral_code': generate_referral_code(user_id),
            'referred_by': None,
            'referrals': [],
            'wallet_balance': 0.0,
            'payment_history': []
        }
    data[str(user_id)].update(updates)
    save_json(user_data_file, data)

def add_referral(referrer_id, referred_id):
    """Add a referral relationship"""
    data = load_json(user_data_file)
    
    # Initialize referred user
    if str(referred_id) not in data:
        data[str(referred_id)] = {
            'name': '',
            'join_date': datetime.now().strftime('%Y-%m-%d'),
            'orders': [],
            'service_orders': [],
            'referral_code': generate_referral_code(referred_id),
            'referred_by': None,
            'referrals': [],
            'wallet_balance': 0.0,
            'payment_history': []
        }
    
    referred_data = data[str(referred_id)]
    
    # Check if already referred
    if referred_data.get('referred_by'):
        return False
    
    # Set referrer
    referred_data['referred_by'] = referrer_id
    
    # Initialize referrer if doesn't exist
    if str(referrer_id) not in data:
        data[str(referrer_id)] = {
            'name': '',
            'join_date': datetime.now().strftime('%Y-%m-%d'),
            'orders': [],
            'service_orders': [],
            'referral_code': generate_referral_code(referrer_id),
            'referred_by': None,
            'referrals': [],
            'wallet_balance': 0.0,
            'payment_history': []
        }
    
    referrer_data = data[str(referrer_id)]
    if 'referrals' not in referrer_data:
        referrer_data['referrals'] = []
    
    # Add to referrer's list
    if referred_id not in referrer_data['referrals']:
        referrer_data['referrals'].append(referred_id)
    
    save_json(user_data_file, data)
    return True

def get_referral_stats(user_id):
    """Get referral statistics for a user"""
    user_data = get_user_data(user_id)
    referrals = user_data.get('referrals', [])
    
    total_referrals = len(referrals)
    active_referrals = 0
    
    for ref_id in referrals:
        ref_data = get_user_data(ref_id)
        if ref_data.get('orders') or ref_data.get('service_orders'):
            active_referrals += 1
    
    return {
        'total': total_referrals,
        'active': active_referrals,
        'code': user_data.get('referral_code', generate_referral_code(user_id))
    }

async def process_referral_reward(user_id, deposit_amount):
    """Process referral reward when a referred user makes a deposit"""
    try:
        user_data = get_user_data(user_id)
        referrer_id = user_data.get('referred_by')
        
        # Check if user was referred by someone
        if not referrer_id:
            return None
        
        # Calculate 25% reward
        reward_amount = round(float(deposit_amount) * 0.25, 2)
        
        # Add reward to referrer's wallet
        referrer_data = get_user_data(referrer_id)
        current_balance = float(referrer_data.get('wallet_balance', 0))
        new_balance = current_balance + reward_amount
        
        # Create payment record for referrer
        payment_record = {
            'amount': reward_amount,
            'type': 'referral_reward',
            'description': f'Referral Reward - User deposited ${deposit_amount:.2f}',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'balance_after': new_balance
        }
        
        referrer_data['wallet_balance'] = new_balance
        if 'payment_history' not in referrer_data:
            referrer_data['payment_history'] = []
        referrer_data['payment_history'].append(payment_record)
        
        update_user_data(referrer_id, referrer_data)
        
        # Get user info for notification
        try:
            user_entity = await bot.get_entity(user_id)
            user_name = user_entity.first_name or "A user"
            
            # Create beautiful notification message
            notification = (
                "🎊 <b>Referral Reward Received!</b> 🎊\n\n"
                "┏━━━━━━━━━━━━━━━━━━━━━┓\n"
                f"┃  💰 <b>+${reward_amount:.2f} USD</b>\n"
                "┗━━━━━━━━━━━━━━━━━━━━━┛\n\n"
                f"🎯 <b>{user_name}</b> just deposited <b>${deposit_amount:.2f}</b>\n"
                f"💸 <b>25% reward</b> has been added to your wallet!\n\n"
                f"📊 <b>New Balance:</b> <code>${new_balance:.2f}</code>\n\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "✨ <i>Keep sharing your referral link to earn more rewards!</i> ✨"
            )
            
            # Send notification to referrer
            await bot.send_message(
                referrer_id,
                notification,
                parse_mode='html'
            )
            
            return reward_amount
            
        except Exception as e:
            log_error(f"Failed to send referral notification to {referrer_id}", e)
            return reward_amount
            
    except Exception as e:
        log_error(f"Failed to process referral reward for user {user_id}", e)
        return None

def calculate_fee(order_total, fee_percentage=None, fee_fixed=None, fee_string=None):
    try:
        total = float(order_total)
        
        # If fee_string is provided (new format like "18%"), parse it
        if fee_string:
            fee_string = fee_string.strip()
            if fee_string.endswith('%'):
                fee_percentage = float(fee_string.replace('%', ''))
                fee_fixed = 0
            else:
                fee_percentage = 18  # default
                fee_fixed = 0
        
        # If neither is provided, use defaults
        if fee_percentage is None:
            fee_percentage = 18
        if fee_fixed is None:
            fee_fixed = 0
            
        fee = (total * fee_percentage / 100) + fee_fixed
        return round(fee, 2)
    except:
        return 0

# Wallet Functions
def add_to_wallet(user_id, amount, description="Deposit"):
    """Add funds to user wallet"""
    try:
        user_data = get_user_data(user_id)
        current_balance = float(user_data.get('wallet_balance', 0))
        new_balance = current_balance + float(amount)
        
        payment_record = {
            'amount': float(amount),
            'type': 'deposit',
            'description': description,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'balance_after': new_balance
        }
        
        user_data['wallet_balance'] = new_balance
        if 'payment_history' not in user_data:
            user_data['payment_history'] = []
        user_data['payment_history'].append(payment_record)
        
        update_user_data(user_id, user_data)
        return True
    except Exception as e:
        log_error(f"Failed to add to wallet for user {user_id}", e)
        return False

def deduct_from_wallet(user_id, amount, description="Purchase"):
    """Deduct funds from user wallet"""
    try:
        user_data = get_user_data(user_id)
        current_balance = float(user_data.get('wallet_balance', 0))
        
        if current_balance < float(amount):
            return False
        
        new_balance = current_balance - float(amount)
        
        payment_record = {
            'amount': -float(amount),
            'type': 'deduction',
            'description': description,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'balance_after': new_balance
        }
        
        user_data['wallet_balance'] = new_balance
        if 'payment_history' not in user_data:
            user_data['payment_history'] = []
        user_data['payment_history'].append(payment_record)
        
        update_user_data(user_id, user_data)
        return True
    except Exception as e:
        log_error(f"Failed to deduct from wallet for user {user_id}", e)
        return False

def get_wallet_balance(user_id):
    """Get user wallet balance"""
    user_data = get_user_data(user_id)
    return float(user_data.get('wallet_balance', 0))

# Payment Functions
async def create_payment(user_id, amount, description, order_id=None):
    """Create OxaPay payment invoice"""
    try:
        if not oxapay:
            log_error("OxaPay not initialized")
            return None, None
            
        payment_order_id = order_id or f"PAY-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create invoice using SyncOxaPay with raw_response=True
        response = oxapay.create_invoice(
            amount=float(amount),
            currency='USD',
            order_id=payment_order_id,
            description=description,
            raw_response=True
        )
        
        if response and response.get("status") == 200:  # Success code
            pay_link = response["data"]["payment_url"]
            track_id = response["data"]["track_id"]
            
            # Save payment record
            payments = load_json(payments_file)
            payments[payment_order_id] = {
                'user_id': user_id,
                'amount': float(amount),
                'description': description,
                'status': 'pending',
                'payment_link': pay_link,
                'track_id': track_id,
                'created_at': datetime.now().isoformat(),
                'order_id': order_id
            }
            save_json(payments_file, payments)
            
            return pay_link, payment_order_id
        else:
            error_msg = response.get("message", "Unknown error") if response else "No response"
            log_error(f"OxaPay create_invoice failed: {error_msg}")
            return None, None
        
    except Exception as e:
        log_error(f"Failed to create payment for user {user_id}", e)
        return None, None

# Add this after the OxaPay initialization (after line with oxapay = SyncOxaPay...)
def test_oxapay_connection():
    """Test OxaPay connection"""
    try:
        # Try to create a test invoice (this should work if key is valid)
        test_response = oxapay.create_invoice(
            amount=1.0,
            currency='USD',
            order_id='TEST-' + datetime.now().strftime('%Y%m%d%H%M%S'),
            description='Test invoice',
            raw_response=True
        )
        if test_response and test_response.get("status") == 200:
            print("✅ OxaPay API test successful!")
            return True
        else:
            print(f"❌ OxaPay API test failed: {test_response}")
            return False
    except Exception as e:
        print(f"❌ OxaPay API test error: {e}")
        return False

# Call the test
if oxapay:
    test_oxapay_connection()

async def check_payment_status(payment_id):
    """Check payment status from OxaPay"""
    try:
        if not oxapay:
            return None
            
        payments = load_json(payments_file)
        if payment_id not in payments:
            return None
        
        track_id = payments[payment_id].get('track_id')
        if not track_id:
            return None
        
        # Check payment info using SyncOxaPay with raw_response=True
        response = oxapay.get_payment_information(track_id=track_id, raw_response=True)
        
        if response and response.get("status") == 200:
            status = response["data"].get('status', '').lower()
            
            # OxaPay status: Waiting, Confirming, Paid, Expired, etc.
            if status in ['paid', 'confirming', 'confirmed']:
                payments[payment_id]['status'] = 'completed'
                save_json(payments_file, payments)
                return 'completed'
            elif status in ['expired', 'canceled', 'failed']:
                payments[payment_id]['status'] = 'failed'
                save_json(payments_file, payments)
                return 'failed'
            elif status in ['waiting', 'pending']:
                return 'pending'
            
            return 'pending'
        
        return None
    except Exception as e:
        log_error(f"Failed to check payment status for {payment_id}", e)
        return None

def format_payment_message(amount, payment_link, payment_id, minutes_remaining=120, title="Deposit Payment", description="Funds will be added automatically", order_id=None):
    """Format payment message with countdown"""
    hours = minutes_remaining // 60
    minutes = minutes_remaining % 60
    
    if hours > 0:
        time_str = f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
    else:
        time_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
    
    message = (
        f"💳 <b>{title}</b>\n\n"
        f"💵 Amount: <b>${amount:.2f} USD</b>\n"
    )
    
    if order_id:
        message += f"🆔 Order: <code>{order_id}</code>\n\n"
    else:
        message += "\n"
    
    message += (
        f"<b>Payment Instructions:</b>\n"
        f"1️⃣ Click the payment link below\n"
        f"2️⃣ Complete the cryptocurrency payment\n"
        f"3️⃣ {description}\n\n"
        f"🔐 <i>Secure payment via OxaPay</i>\n"
        f"⏱ <i>Payment expires in {time_str}</i>\n\n"
        f"🆔 Payment ID: <code>{payment_id}</code>"
    )
    
    return message

async def show_payment_countdown(msg_or_event, user_id, amount, payment_link, payment_id, payment_type='deposit', title="Deposit Payment", description="Funds will be added automatically", order_id=None, check_button_data=None):
    """Show payment message with live countdown from 120 minutes to 0, and auto-confirm on payment"""
    try:
        check_button = check_button_data or f"check_payment_{payment_id}"
        buttons = [
            [Button.url("💳 Pay Now", payment_link)],
            [Button.inline("🔄 Check Payment Status", check_button.encode())],
            [Button.inline("🏠 Main Menu", b"main_menu")]
        ]
        
        # Countdown from 119 to 0 (every minute = 60 seconds)
        for remaining_minutes in range(119, -1, -1):
            await asyncio.sleep(60)  # Wait 1 minute
            
            # Check if payment was completed
            status = await check_payment_status(payment_id)
            if status == 'completed':
                # Auto-confirm payment
                if payment_type == 'deposit':
                    payments = load_json(payments_file)
                    if payment_id in payments:
                        payment_data = payments[payment_id]
                        if payment_data['status'] == 'completed':
                            user_data = get_user_data(user_id)
                            user_data['wallet_balance'] = user_data.get('wallet_balance', 0) + payment_data['amount']
                            save_json(user_data_file, {str(user_id): user_data})
                            
                            success_message = (
                                f"✅ <b>Payment Confirmed!</b>\n\n"
                                f"💵 Amount: <b>${payment_data['amount']:.2f} USD</b>\n"
                                f"💰 New Balance: <b>${user_data['wallet_balance']:.2f} USD</b>\n\n"
                                f"<i>Funds have been added to your wallet automatically.</i>"
                            )
                            try:
                                if hasattr(msg_or_event, 'edit'):
                                    await msg_or_event.edit(success_message, buttons=[[Button.inline("🏠 Main Menu", b"main_menu")]], parse_mode='html')
                                else:
                                    await bot.send_message(user_id, success_message, buttons=[[Button.inline("🏠 Main Menu", b"main_menu")]], parse_mode='html')
                            except:
                                pass
                            return
                # Handle other payment types (orders, services, etc.) similarly
                return
            
            try:
                if remaining_minutes > 0:
                    updated_message = format_payment_message(amount, payment_link, payment_id, remaining_minutes, title, description, order_id)
                    if hasattr(msg_or_event, 'edit'):
                        await msg_or_event.edit(updated_message, buttons=buttons, parse_mode='html')
                    else:
                        # If it's a Message object, edit it
                        await msg_or_event.edit(updated_message, buttons=buttons, parse_mode='html')
                else:
                    # Show expired message
                    expired_message = (
                        f"💳 <b>{title}</b>\n\n"
                        f"💵 Amount: <b>${amount:.2f} USD</b>\n\n"
                        f"❌ <b>Payment expired</b>\n\n"
                        f"⏱ <i>This payment link has expired. Please create a new payment.</i>\n\n"
                        f"🆔 Payment ID: <code>{payment_id}</code>"
                    )
                    if hasattr(msg_or_event, 'edit'):
                        await msg_or_event.edit(expired_message, buttons=[[Button.inline("🏠 Main Menu", b"main_menu")]], parse_mode='html')
                    else:
                        await msg_or_event.edit(expired_message, buttons=[[Button.inline("🏠 Main Menu", b"main_menu")]], parse_mode='html')
            except Exception as e:
                # Message might be deleted or modified by user
                break
                
    except Exception as e:
        log_error("Payment countdown update error", e)

# Order Functions
def create_order(user_id, store_info, order_data):
    orders = load_json(orders_file)
    order_id = f"ORD-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    orders[order_id] = {
        'user_id': user_id,
        'store_info': store_info,
        'order_data': order_data,
        'status': 'pending',
        'payment_status': 'unpaid',
        'remarks': [],
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'created_at': datetime.now().isoformat()
    }
    
    save_json(orders_file, orders)
    
    user_data = get_user_data(user_id)
    user_data['orders'].append(order_id)
    update_user_data(user_id, user_data)
    
    return order_id

def get_order(order_id):
    orders = load_json(orders_file)
    return orders.get(order_id)

def update_order(order_id, updates):
    orders = load_json(orders_file)
    if order_id in orders:
        orders[order_id].update(updates)
        save_json(orders_file, orders)
        return True
    return False

def add_order_remark(order_id, remark, by_admin=True):
    orders = load_json(orders_file)
    if order_id in orders:
        orders[order_id]['remarks'].append({
            'text': remark,
            'by': 'Admin' if by_admin else 'Customer',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_json(orders_file, orders)
        return True
    return False

# Service Order Functions
def create_service_order(user_id, service_type, service_name, price, order_data=None):
    """Create a service order (aged accounts, boxing, etc.)"""
    service_orders = load_json(service_orders_file)
    order_id = f"SRV-{service_type[:3].upper()}-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    service_orders[order_id] = {
        'user_id': user_id,
        'service_type': service_type,
        'service_name': service_name,
        'price': price,
        'order_data': order_data or {},
        'status': 'pending',
        'payment_status': 'unpaid',
        'delivery_content': None,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'created_at': datetime.now().isoformat()
    }
    
    save_json(service_orders_file, service_orders)
    
    user_data = get_user_data(user_id)
    if 'service_orders' not in user_data:
        user_data['service_orders'] = []
    user_data['service_orders'].append(order_id)
    update_user_data(user_id, user_data)
    
    return order_id

def get_service_order(order_id):
    service_orders = load_json(service_orders_file)
    return service_orders.get(order_id)

def update_service_order(order_id, updates):
    service_orders = load_json(service_orders_file)
    if order_id in service_orders:
        service_orders[order_id].update(updates)
        save_json(service_orders_file, service_orders)
        return True
    return False

# Ticket functions
def create_ticket(user_id, question, user_name):
    tickets = load_json(tickets_file)
    ticket_id = f"TKT-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    tickets[ticket_id] = {
        'user_id': user_id,
        'user_name': user_name,
        'question': question,
        'status': 'pending',
        'messages': [],
        'created_at': datetime.now().isoformat(),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    save_json(tickets_file, tickets)
    return ticket_id

def get_ticket(ticket_id):
    tickets = load_json(tickets_file)
    return tickets.get(ticket_id)

def update_ticket(ticket_id, updates):
    tickets = load_json(tickets_file)
    if ticket_id in tickets:
        tickets[ticket_id].update(updates)
        save_json(tickets_file, tickets)
        return True
    return False

def get_active_ticket_for_user(user_id):
    tickets = load_json(tickets_file)
    for tid, ticket in tickets.items():
        if ticket['user_id'] == user_id and ticket['status'] == 'active':
            return tid
    return None

def add_ticket_message(ticket_id, message, from_admin=False):
    tickets = load_json(tickets_file)
    if ticket_id in tickets:
        tickets[ticket_id]['messages'].append({
            'text': message,
            'from': 'admin' if from_admin else 'user',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        save_json(tickets_file, tickets)
        return True
    return False

# Raffle functions
def create_raffle(prize, winners_count, duration_minutes):
    raffles = load_json(raffles_file)
    raffle_id = f"RAF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    
    raffles[raffle_id] = {
        'prize': prize,
        'winners_count': winners_count,
        'participants': [],
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'end_time': end_time.isoformat(),
        'winners': []
    }
    
    save_json(raffles_file, raffles)
    return raffle_id

def get_raffle(raffle_id):
    raffles = load_json(raffles_file)
    return raffles.get(raffle_id)

def join_raffle(raffle_id, user_id):
    raffles = load_json(raffles_file)
    if raffle_id in raffles:
        raffle = raffles[raffle_id]
        if raffle['status'] == 'active' and user_id not in raffle['participants']:
            raffle['participants'].append(user_id)
            save_json(raffles_file, raffles)
            return True
    return False

def get_active_raffles():
    raffles = load_json(raffles_file)
    active = []
    for rid, raffle in raffles.items():
        if raffle['status'] == 'active':
            end_time = datetime.fromisoformat(raffle['end_time'])
            if datetime.now() < end_time:
                active.append(rid)
            else:
                raffle['status'] = 'ended'
                save_json(raffles_file, raffles)
    return active

async def end_raffle(raffle_id):
    raffles = load_json(raffles_file)
    if raffle_id not in raffles:
        return False
    
    raffle = raffles[raffle_id]
    if raffle['status'] != 'active':
        return False
    
    participants = raffle['participants']
    winners_count = min(raffle['winners_count'], len(participants))
    
    if winners_count > 0:
        winners = random.sample(participants, winners_count)
        raffle['winners'] = winners
    else:
        raffle['winners'] = []
    
    raffle['status'] = 'ended'
    save_json(raffles_file, raffles)
    
    if raffle['winners']:
        winner_mentions = []
        for winner_id in raffle['winners']:
            try:
                user = await bot.get_entity(winner_id)
                user_name = user.first_name or "User"
                winner_mentions.append(f"• <a href='tg://user?id={winner_id}'>{user_name}</a>")
            except:
                winner_mentions.append(f"• User {winner_id}")
        
        announcement = (
            f"🎉 <b>Raffle Ended!</b>\n\n"
            f"🎁 Prize: <b>{raffle['prize']}</b>\n"
            f"👥 Participants: {len(participants)}\n\n"
            f"🏆 <b>Winners:</b>\n"
            + "\n".join(winner_mentions) +
            f"\n\n<i>Congratulations to all winners!</i>"
        )
    else:
        announcement = (
            f"🎉 <b>Raffle Ended!</b>\n\n"
            f"🎁 Prize: <b>{raffle['prize']}</b>\n\n"
            f"❌ <i>No participants joined this raffle.</i>"
        )
    
    try:
        await bot.send_message(VOUCHES_CHANNEL_ID, announcement, parse_mode='html')
    except Exception as e:
        log_error(f"Failed to announce raffle winners: {e}", e)
    
    return True

async def raffle_monitor():
    """Background task to monitor and end raffles"""
    while True:
        try:
            raffles = load_json(raffles_file)
            for raffle_id, raffle in raffles.items():
                if raffle['status'] == 'active':
                    end_time = datetime.fromisoformat(raffle['end_time'])
                    if datetime.now() >= end_time:
                        await end_raffle(raffle_id)
            
            await asyncio.sleep(30)
        except Exception as e:
            log_error("Raffle monitor error", e)
            await asyncio.sleep(60)

async def verification_cleanup():
    """Background task to clean up expired verifications"""
    while True:
        try:
            current_time = datetime.now()
            expired_users = []
            
            # Find expired verifications
            for user_id, verification_time in verified_users.items():
                time_elapsed = (current_time - verification_time).total_seconds()
                if time_elapsed >= 60:  # Verification expired
                    expired_users.append(user_id)
            
            # Remove expired verifications
            for user_id in expired_users:
                del verified_users[user_id]
            
            if expired_users:
                print(f"Cleaned up {len(expired_users)} expired verifications")
            
            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            log_error("Verification cleanup error", e)
            await asyncio.sleep(60)

async def ticket_expiration_monitor():
    """Background task to monitor and expire tickets that haven't been accepted in 24 hours"""
    while True:
        try:
            tickets = load_json(tickets_file)
            current_time = datetime.now()
            expired_tickets = []
            
            # Check all pending tickets
            for ticket_id, ticket in tickets.items():
                if ticket['status'] == 'pending':
                    created_at = datetime.fromisoformat(ticket['created_at'])
                    time_elapsed = (current_time - created_at).total_seconds()
                    
                    # If ticket is older than 24 hours (86400 seconds)
                    if time_elapsed >= 86400:
                        # Mark as expired
                        if update_ticket(ticket_id, {'status': 'expired'}):
                            expired_tickets.append(ticket_id)
                            
                            # Notify the user who created the ticket
                            try:
                                await bot.send_message(
                                    ticket['user_id'],
                                    f"⏰ <b>Ticket Expired</b>\n\n"
                                    f"🎫 Ticket: <code>{ticket_id}</code>\n\n"
                                    f"<i>Your support ticket was not accepted by an admin within 24 hours and has expired.</i>\n\n"
                                    f"<i>Please create a new ticket if you still need assistance.</i>",
                                    parse_mode='html'
                                )
                            except Exception as e:
                                log_error(f"Failed to notify user about expired ticket {ticket_id}", e)
                            
                            # Notify all admins
                            try:
                                user_link = f"<a href='tg://user?id={ticket['user_id']}'>{ticket['user_name']}</a>"
                                await notify_admins(
                                    f"⏰ <b>Ticket Expired</b>\n\n"
                                    f"🎫 Ticket: <code>{ticket_id}</code>\n"
                                    f"👤 User: {user_link}\n"
                                    f"🆔 User ID: <code>{ticket['user_id']}</code>\n\n"
                                    f"<i>This ticket was not accepted within 24 hours and has expired.</i>",
                                    parse_mode='html'
                                )
                            except Exception as e:
                                log_error(f"Failed to notify admins about expired ticket {ticket_id}", e)
            
            if expired_tickets:
                print(f"Expired {len(expired_tickets)} tickets")
            
            await asyncio.sleep(3600)  # Check every hour
        except Exception as e:
            log_error("Ticket expiration monitor error", e)
            await asyncio.sleep(3600)

async def send_main_menu(chat_id, edit_message=None):
    try:
        sender = await bot.get_entity(chat_id)
        username = sender.first_name if sender.first_name else "there"
        
        message = (
            f"✨ <b>Welcome back, {username}!</b>\n\n"
            f"<b>Return's Portal</b> — Your gateway to premium services\n"
            f"⚡ <i>$2M+ processed • Trusted since 2023 • #1 Provider on the market</i>\n\n"
            f"👇 <b>Select what you need:</b>"
        )
        
        buttons = [
            [Button.inline("🛍️ Store List", b"store_list"), Button.inline("💡 Help & FAQ", b"faqs")],
            [Button.inline("👨‍💼 My Account", b"profile"), Button.inline("🔗 Links", b"links_menu")],
            [Button.inline("🎉 Active Giveaways", b"raffles"), Button.inline("⭐ Reviews", b"vouches")],
            [Button.inline("🏷 Other Services", b"other_services"), Button.inline("📞 Contact Support", b"support")],
            [Button.inline("🌟 Refund Method Store", b"method_store")]
        ]
        
        if is_admin(chat_id):
            buttons.append([Button.inline("🔧 Admin Panel", b"admin_panel")])
        
        banner_path = "Banner.jpg"
        
        if os.path.exists(banner_path):
            await bot.send_file(
                chat_id,
                banner_path,
                caption=message,
                buttons=buttons,
                parse_mode='html'
            )
        else:
            await bot.send_message(
                chat_id,
                message,
                buttons=buttons,
                parse_mode='html'
            )
    except Exception as e:
        log_error(f"Error in send_main_menu for {chat_id}", e)

# Welcome handler
@bot.on(events.ChatAction)
async def welcome_handler(event):
    try:
        if event.chat_id != GROUP_ID:
            return
        
        if event.user_joined:
            user = await event.get_user()
            if user.bot:
                return
                
            user_name = user.first_name if user.first_name else "there"
            
            welcome_message = (
                f"🎉 <b>Welcome to Return's Portal, {user_name}!</b>\n\n"
                f"🌟 We're glad to have you here!\n\n"
                f"<b>What we offer:</b>\n"
                f"• 📦 60+ Premium Stores\n"
                f"• 🔥 Exclusive Monthly Promos\n"
                f"• 💬 24/7 Support & Therapy Chat\n"
                f"• ⭐ Verified Reviews & Vouches\n\n"
                f"<b>Quick Start:</b>\n"
                f"• Use /start in bot DM for full store list\n"
                f"• Read pinned messages for important updates\n"
                f"• Feel free to ask questions anytime!\n\n"
                f"⚡ <i>1.5+ years in business • 2M+ orders processed • Fastest service on the market!</i>\n\n"
                f"🚀 Let's get started!"
            )
            
            await bot.send_message(GROUP_ID, welcome_message, parse_mode='html')
    except Exception as e:
        log_error("Welcome handler error", e)

# Captcha and Invite Link Functions
def generate_captcha():
    """Generate a simple math captcha"""
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    answer = num1 + num2
    question = f"{num1} + {num2} = ?"
    return question, answer

async def generate_invite_links():
    """Generate temporary invite links for all channels with auto-revoke after 60s"""
    try:
        links = {}
        invite_objects = {}
        channels = {
            'main_channel': -1002919289402,
            'vouches': -1002919289402,
            'method_updates': -1002919289402,
            'public_chat': -1002919289402
        }
        
        for name, channel_id in channels.items():
            try:
                # Create invite link with 60 second expiry and usage limit of 1
                result = await bot(ExportChatInviteRequest(
                    peer=channel_id,
                    expire_date=int((datetime.now() + timedelta(seconds=60)).timestamp()),
                    usage_limit=1
                ))
                links[name] = result.link
                invite_objects[name] = {'link': result.link, 'channel_id': channel_id}
            except Exception as e:
                log_error(f"Failed to create invite link for {name} ({channel_id})", e)
                links[name] = None
        
        # Schedule auto-revoke after 60 seconds
        asyncio.create_task(revoke_invite_links(invite_objects, 60))
        
        return links
    except Exception as e:
        log_error("Failed to generate invite links", e)
        return None

async def generate_all_invite_links():
    """Generate temporary invite links for ALL channels (4 total) with auto-revoke after 60s"""
    try:
        links = {}
        invite_objects = {}
        channels = {
            'main_channel': -1002919289402,
            'vouches': -1002919289402,
            'method_updates': -1002919289402,
            'public_chat': -1002919289402
        }
        
        for name, channel_id in channels.items():
            try:
                # Create invite link with 60 second expiry and usage limit of 1
                result = await bot(ExportChatInviteRequest(
                    peer=channel_id,
                    expire_date=int((datetime.now() + timedelta(seconds=60)).timestamp()),
                    usage_limit=1
                ))
                links[name] = result.link
                invite_objects[name] = {'link': result.link, 'channel_id': channel_id}
            except Exception as e:
                log_error(f"Failed to create invite link for {name} ({channel_id})", e)
                links[name] = None
        
        # Schedule auto-revoke after 60 seconds
        asyncio.create_task(revoke_invite_links(invite_objects, 60))
        
        return links
    except Exception as e:
        log_error("Failed to generate all invite links", e)
        return None

async def revoke_invite_links(invite_objects, delay):
    """Auto-revoke invite links after specified delay"""
    try:
        await asyncio.sleep(delay)
        
        from telethon.tl.functions.messages import DeleteExportedChatInviteRequest
        
        for name, data in invite_objects.items():
            try:
                await bot(DeleteExportedChatInviteRequest(
                    peer=data['channel_id'],
                    link=data['link']
                ))
                print(f"[CLEANUP] Revoked invite link for {name}")
            except Exception as e:
                # Link might already be expired or used
                print(f"[CLEANUP] Could not revoke {name} link (likely expired): {e}")
    except Exception as e:
        log_error("Failed to revoke invite links", e)

async def format_invite_message(links, countdown=60):
    """Format the invite links message with countdown - handles missing links gracefully"""
    if not links:
        return None
    
    # Build message with only successfully generated links
    message_parts = [
        "✨ <b>Welcome to Return's Portal!</b> ✨\n\n",
        "📨 <b>Your Invite Links</b>\n",
        f"⏰ <b>Expires in: {countdown} seconds</b>\n\n"
    ]
    
    if links.get('main_channel'):
        message_parts.append(f"📢 <b>Main Channel:</b>\n{links['main_channel']}\n\n")
    
    if links.get('vouches'):
        message_parts.append(f"⭐ <b>Vouches:</b>\n{links['vouches']}\n\n")
    
    if links.get('method_updates'):
        message_parts.append(f"🛍 <b>Methods Bot Updates:</b>\n{links['method_updates']}\n\n")
    
    if links.get('public_chat'):
        message_parts.append(f"💬 <b>Public Chat:</b>\n{links['public_chat']}\n\n")
    
    # Check if we have at least one link
    if len([k for k, v in links.items() if v]) == 0:
        return None
    
    message_parts.extend([
        "📋 <b>Quick Steps:</b>\n\n",
        "1️⃣ Click each link above\n",
        "2️⃣ Join all channels\n",
        "3️⃣ If you miss any, type /start again\n",
        "4️⃣ Click the button below to browse stores\n\n",
        f"⚡ <i>Hurry! Links expire in {countdown} seconds!</i>"
    ])
    
    return ''.join(message_parts)

async def format_all_links_message(links, countdown=60):
    """Format ALL invite links message (4 channels) with countdown - handles missing links gracefully"""
    if not links:
        return None
    
    # Build message with only successfully generated links
    message_parts = [
        "✨ <b>Welcome to Return's Portal!</b> ✨\n\n",
        "📨 <b>Your Invite Links</b>\n",
        f"⏰ <b>Expires in: {countdown} seconds</b>\n\n"
    ]
    
    if links.get('main_channel'):
        message_parts.append(f"📢 <b>Main Channel:</b>\n{links['main_channel']}\n\n")
    
    if links.get('vouches'):
        message_parts.append(f"⭐ <b>Vouches:</b>\n{links['vouches']}\n\n")
    
    if links.get('method_updates'):
        message_parts.append(f"🛍 <b>Methods Bot Updates:</b>\n{links['method_updates']}\n\n")
    
    if links.get('public_chat'):
        message_parts.append(f"💬 <b>Public Chat:</b>\n{links['public_chat']}\n\n")
    
    # Check if we have at least one link
    if len([k for k, v in links.items() if v]) == 0:
        return None
    
    message_parts.extend([
        "📋 <b>Quick Steps:</b>\n\n",
        "1️⃣ Click each link above\n",
        "2️⃣ Join all channels\n",
        "3️⃣ If you miss any, type /start again\n",
        "4️⃣ Click the button below to browse stores\n\n",
        f"⚡ <i>Hurry! Links expire in {countdown} seconds!</i>"
    ])
    
    return ''.join(message_parts)

async def show_invite_with_countdown(event, links, buttons, is_edit=False):
    """Show invite message with live countdown from 60 to 1"""
    try:
        # Send or edit initial message
        invite_message = await format_invite_message(links, 60)
        if not invite_message:
            # If no message could be generated (all links failed), show error
            error_msg = "❌ <b>Failed to generate invite links</b>\n\n<i>Please try again later or contact support.</i>"
            if is_edit:
                try:
                    await event.edit(error_msg, buttons=buttons, parse_mode='html')
                except:
                    pass
            else:
                try:
                    await event.respond(error_msg, buttons=buttons, parse_mode='html')
                except:
                    pass
            return
        
        if is_edit:
            try:
                await event.edit(invite_message, buttons=buttons, parse_mode='html', link_preview=False)
                msg = event
            except:
                return
        else:
            msg = await event.respond(invite_message, buttons=buttons, parse_mode='html', link_preview=False)
        
        # Countdown from 59 to 0 (every second)
        for remaining in range(59, -1, -1):
            await asyncio.sleep(1)
            try:
                if remaining > 0:
                    updated_message = await format_invite_message(links, remaining)
                    if updated_message:  # Only update if message is valid
                        await msg.edit(updated_message, buttons=buttons, parse_mode='html', link_preview=False)
                else:
                    # Show expired message
                    expired_message = (
                        "✨ <b>Welcome to Return's Portal!</b> ✨\n\n"
                        "📨 <b>Your Invite Links</b>\n\n"
                        "❌ <b>Links expired</b>\n\n"
                        "💡 <i>Click the Links button again to get new invite links.</i>"
                    )
                    await msg.edit(expired_message, buttons=buttons, parse_mode='html', link_preview=False)
            except Exception as e:
                # Message might be deleted or modified by user, or rate limited
                break
                
    except Exception as e:
        log_error("Countdown update error", e)

async def show_all_links_with_countdown(event, links, buttons, is_edit=False):
    """Show ALL links message with live countdown from 60 to 1"""
    try:
        # Send or edit initial message
        invite_message = await format_all_links_message(links, 60)
        if not invite_message:
            # If no message could be generated (all links failed), show error
            error_msg = "❌ <b>Failed to generate invite links</b>\n\n<i>Please try again later or contact support.</i>"
            if is_edit:
                try:
                    await event.edit(error_msg, buttons=buttons, parse_mode='html')
                except:
                    pass
            else:
                try:
                    await event.respond(error_msg, buttons=buttons, parse_mode='html')
                except:
                    pass
            return
        
        if is_edit:
            try:
                await event.edit(invite_message, buttons=buttons, parse_mode='html', link_preview=False)
                msg = event
            except:
                return
        else:
            msg = await event.respond(invite_message, buttons=buttons, parse_mode='html', link_preview=False)
        
        # Countdown from 59 to 0 (every second)
        for remaining in range(59, -1, -1):
            await asyncio.sleep(1)
            try:
                if remaining > 0:
                    updated_message = await format_all_links_message(links, remaining)
                    if updated_message:  # Only update if message is valid
                        await msg.edit(updated_message, buttons=buttons, parse_mode='html', link_preview=False)
                else:
                    # Show expired message
                    expired_message = (
                        "✨ <b>Welcome to Return's Portal!</b> ✨\n\n"
                        "📨 <b>Your Invite Links</b>\n\n"
                        "❌ <b>Links expired</b>\n\n"
                        "💡 <i>Click the Links button again to get new invite links.</i>"
                    )
                    await msg.edit(expired_message, buttons=buttons, parse_mode='html', link_preview=False)
            except Exception as e:
                # Message might be deleted or modified by user, or rate limited
                break
                
    except Exception as e:
        log_error("All links countdown update error", e)

# Start command with referral support
@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    try:
        user_id = event.sender_id
        save_user(user_id)
        
        sender = await event.get_sender()
        username = sender.first_name if sender.first_name else "there"
        full_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
        user_username = sender.username or "No username"
        
        # Log user starting the bot
        await send_log_to_channel(
            "🚀 BOT START",
            f"User started the bot\nUsername: @{user_username}\nFull Name: {full_name}",
            user_id=user_id,
            username=full_name
        )
        
        # Store referral code for later use
        ref_code = None
        try:
            command_parts = event.message.text.split()
            if len(command_parts) > 1:
                ref_code = command_parts[1].strip()
        except:
            pass
        
        # Check if user has failed captcha recently
        if user_id in captcha_states and captcha_states[user_id].get('failed_at'):
            failed_at = captcha_states[user_id]['failed_at']
            time_elapsed = (datetime.now() - failed_at).total_seconds()
            
            if time_elapsed < 60:
                remaining = int(60 - time_elapsed)
                await event.respond(
                    f"⏳ <b>Please wait {remaining}s before retrying.</b>",
                    parse_mode='html'
                )
                return
            else:
                # Timeout expired, clear failed_at and generate new captcha
                del captcha_states[user_id]
        
        # Check if user has passed captcha (and verification hasn't expired)
        verification_valid = False
        if user_id in verified_users:
            verification_time = verified_users[user_id]
            time_elapsed = (datetime.now() - verification_time).total_seconds()
            if time_elapsed < 60:  # Links are valid for 60 seconds
                verification_valid = True
            else:
                # Verification expired, remove from verified_users
                del verified_users[user_id]
        
        if not verification_valid:
            # Show captcha only (no banner yet)
            question, answer = generate_captcha()
            
            # Store captcha data
            captcha_states[user_id] = {
                'answer': answer,
                'failed_at': None,
                'ref_code': ref_code
            }
            
            # Send captcha message
            captcha_message = (
                f"🔒 <b>Solve to get invites:</b>\n"
                f"<code>{question}</code>"
            )
            await event.respond(captcha_message, parse_mode='html')
            return
        
        # User has passed captcha, show main menu
        # Handle referral code if stored
        if user_id in captcha_states and captcha_states[user_id].get('ref_code'):
            ref_code = captcha_states[user_id]['ref_code']
            
            try:
                all_user_data = load_json(user_data_file)
                referrer_id = None
                
                # Find referrer by code
                for uid, data in all_user_data.items():
                    if data.get('referral_code') == ref_code:
                        referrer_id = int(uid)
                        break
                
                if referrer_id and referrer_id != user_id:
                    if add_referral(referrer_id, user_id):
                        try:
                            referrer_entity = await bot.get_entity(referrer_id)
                            referrer_name = referrer_entity.first_name or "User"
                            
                            # Notify referrer
                            await bot.send_message(
                                referrer_id,
                                f"🎉 <b>New Referral!</b>\n\n"
                                f"👤 <b>{username}</b> just joined using your referral link!\n\n"
                                f"💰 <i>Keep sharing to earn more rewards!</i>",
                                parse_mode='html'
                            )
                        except Exception as e:
                            log_error(f"Failed to notify referrer {referrer_id}", e)
                
                # Clear ref code after processing
                captcha_states[user_id]['ref_code'] = None
            except Exception as e:
                log_error("Referral code processing error", e)
        
        # Update user name if not set
        user_data = get_user_data(user_id)
        if not user_data['name']:
            update_user_data(user_id, {'name': username})
        
        # Send main menu (with proper format and banner)
        await send_main_menu(user_id)
    except Exception as e:
        log_error("Start handler error", e)

# Captcha response handler
def should_handle_captcha(event):
    user_id = event.sender_id
    # Check if user has captcha state and hasn't been verified
    if user_id not in captcha_states or not captcha_states[user_id].get('answer'):
        return False
    if not event.message.text or event.message.text.startswith('/'):
        return False
    # Check if user is verified and verification is still valid
    if user_id in verified_users:
        verification_time = verified_users[user_id]
        time_elapsed = (datetime.now() - verification_time).total_seconds()
        if time_elapsed < 60:  # Still verified
            return False
        else:
            # Verification expired, allow captcha handling
            del verified_users[user_id]
    return True

@bot.on(events.NewMessage(func=should_handle_captcha))
async def captcha_response_handler(event):
    try:
        user_id = event.sender_id
        
        # Double check to prevent duplicate processing
        if user_id not in captcha_states:
            return
        
        # Check if user is already verified and verification is still valid
        if user_id in verified_users:
            verification_time = verified_users[user_id]
            time_elapsed = (datetime.now() - verification_time).total_seconds()
            if time_elapsed < 60:  # Still verified
                return
        
        # Check if user is in timeout
        if captcha_states[user_id].get('failed_at'):
            failed_at = captcha_states[user_id]['failed_at']
            time_elapsed = (datetime.now() - failed_at).total_seconds()
            
            if time_elapsed < 60:
                remaining = int(60 - time_elapsed)
                await event.respond(
                    f"⏳ <b>Please wait {remaining}s before retrying.</b>",
                    parse_mode='html'
                )
                return
            else:
                # Timeout expired, clear the failed_at
                captcha_states[user_id]['failed_at'] = None
        
        user_answer = event.message.text.strip()
        correct_answer = str(captcha_states[user_id]['answer'])
        
        if user_answer == correct_answer:
            # Correct answer - generate invite links
            await event.respond(
                "✅ <b>Correct—fetching invites…</b>",
                parse_mode='html'
            )
            
            # Generate invite links
            links = await generate_invite_links()
            
            if links:
                buttons = [
                    [Button.inline("Browse Return's Hub ⚡️", b"browse_hub")]
                ]
                
                # Show invite with countdown in background
                asyncio.create_task(show_invite_with_countdown(event, links, buttons, is_edit=False))
                
                # Mark user as verified with timestamp and clear captcha state
                verified_users[user_id] = datetime.now()
                captcha_states[user_id]['answer'] = None  # Clear to prevent any further triggers
            else:
                await event.respond(
                    "❌ <b>Failed to generate invite links. Please try again later.</b>",
                    parse_mode='html'
                )
        else:
            # Wrong answer - set timeout and clear answer to prevent repeated triggers
            captcha_states[user_id]['failed_at'] = datetime.now()
            captcha_states[user_id]['answer'] = None  # Clear to prevent handler from triggering again
            await event.respond(
                "❌ <b>Wrong—wait 1 minute.</b>",
                parse_mode='html'
            )
            
    except Exception as e:
        log_error("Captcha response handler error", e)

# Balance command
@bot.on(events.NewMessage(pattern='/balance'))
async def balance_handler(event):
    try:
        user_id = event.sender_id
        balance = get_wallet_balance(user_id)
        
        message = (
            f"💰 <b>Your Wallet Balance</b>\n\n"
            f"💵 Current Balance: <b>${balance:.2f} USD</b>\n\n"
            f"<i>Use the Profile menu to deposit or view payment history</i>"
        )
        
        buttons = [
            [Button.inline("💳 Deposit Funds", b"wallet_deposit")],
            [Button.inline("📊 Payment History", b"payment_history")],
            [Button.inline("🏠 Main Menu", b"main_menu")]
        ]
        
        await event.respond(message, buttons=buttons, parse_mode='html')
    except Exception as e:
        log_error("Balance handler error", e)

# Admin commands
@bot.on(events.NewMessage(pattern=r'^/ban'))
async def ban_handler(event):
    try:
        if not is_admin(event.sender_id):
            return
        
        if event.chat_id != GROUP_ID:
            await event.respond("❌ This command only works in the designated group!")
            return
        
        user_to_ban = None
        
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            user_to_ban = reply_msg.sender_id
            
            bot_me = await bot.get_me()
            if user_to_ban == bot_me.id:
                await event.respond("😅 I can't ban myself!")
                return
        else:
            args = event.message.text.split()[1:]
            if not args:
                await event.respond("❌ Usage: `/ban @username` or `/ban user_id` or reply to a message with `/ban`")
                return
            
            target = args[0]
            if target.startswith('@'):
                user_to_ban = target
            else:
                try:
                    user_to_ban = int(target)
                except ValueError:
                    await event.respond("❌ Invalid user ID!")
                    return
        
        await bot.edit_permissions(GROUP_ID, user_to_ban, view_messages=False)
        await event.respond(f"✅ User banned successfully!")
        
    except Exception as e:
        log_error("Ban error", e)
        await event.respond(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern=r'^/unban'))
async def unban_handler(event):
    try:
        if not is_admin(event.sender_id):
            return
        
        if event.chat_id != GROUP_ID:
            await event.respond("❌ This command only works in the designated group!")
            return
        
        user_to_unban = None
        
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            user_to_unban = reply_msg.sender_id
        else:
            args = event.message.text.split()[1:]
            if not args:
                await event.respond("❌ Usage: `/unban @username` or `/unban user_id`")
                return
            
            target = args[0]
            if target.startswith('@'):
                user_to_unban = target
            else:
                try:
                    user_to_unban = int(target)
                except ValueError:
                    await event.respond("❌ Invalid user ID!")
                    return
        
        await bot.edit_permissions(
            GROUP_ID, user_to_unban,
            view_messages=True, send_messages=True,
            send_media=True, send_stickers=True, send_polls=True
        )
        await event.respond(f"✅ User unbanned successfully!")
        
    except Exception as e:
        log_error("Unban error", e)
        await event.respond(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern=r'^/mute'))
async def mute_handler(event):
    try:
        if not is_admin(event.sender_id):
            return
        
        if event.chat_id != GROUP_ID:
            await event.respond("❌ This command only works in the designated group!")
            return
        
        args = event.message.text.split()[1:]
        duration = None
        user_to_mute = None
        until_date = None
        
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            user_to_mute = reply_msg.sender_id
            
            bot_me = await bot.get_me()
            if user_to_mute == bot_me.id:
                await event.respond("😅 I can't mute myself!")
                return
            
            if args:
                try:
                    duration = int(args[0])
                    until_date = datetime.now() + timedelta(minutes=duration)
                except ValueError:
                    await event.respond("❌ Invalid duration!")
                    return
        else:
            if len(args) == 0:
                await event.respond("❌ Usage: `/mute @username [duration]`")
                return
            
            target = args[0]
            if len(args) >= 2:
                try:
                    duration = int(args[1])
                    until_date = datetime.now() + timedelta(minutes=duration)
                except ValueError:
                    await event.respond("❌ Invalid duration!")
                    return
            
            if target.startswith('@'):
                user_to_mute = target
            else:
                try:
                    user_to_mute = int(target)
                except ValueError:
                    await event.respond("❌ Invalid user ID!")
                    return
        
        if until_date:
            await bot.edit_permissions(
                GROUP_ID, user_to_mute, until_date=until_date,
                send_messages=False, send_media=False,
                send_stickers=False, send_polls=False
            )
            await event.respond(f"✅ User muted for {duration} minute(s)!")
        else:
            await bot.edit_permissions(
                GROUP_ID, user_to_mute,
                send_messages=False, send_media=False,
                send_stickers=False, send_polls=False
            )
            await event.respond(f"✅ User muted permanently!")
        
    except Exception as e:
        log_error("Mute error", e)
        await event.respond(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern=r'^/unmute'))
async def unmute_handler(event):
    try:
        if not is_admin(event.sender_id):
            return
        
        if event.chat_id != GROUP_ID:
            await event.respond("❌ This command only works in the designated group!")
            return
        
        user_to_unmute = None
        
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            user_to_unmute = reply_msg.sender_id
        else:
            args = event.message.text.split()[1:]
            if not args:
                await event.respond("❌ Usage: `/unmute @username` or `/unmute user_id`")
                return
            
            target = args[0]
            if target.startswith('@'):
                user_to_unmute = target
            else:
                try:
                    user_to_unmute = int(target)
                except ValueError:
                    await event.respond("❌ Invalid user ID!")
                    return
        
        await bot.edit_permissions(
            GROUP_ID, user_to_unmute,
            send_messages=True, send_media=True,
            send_stickers=True, send_polls=True
        )
        await event.respond(f"✅ User unmuted successfully!")
        
    except Exception as e:
        log_error("Unmute error", e)
        await event.respond(f"❌ Error: {str(e)}")

@bot.on(events.NewMessage(pattern=r'^/kick'))
async def kick_handler(event):
    try:
        if not is_admin(event.sender_id):
            return
        
        if event.chat_id != GROUP_ID:
            await event.respond("❌ This command only works in the designated group!")
            return
        
        user_to_kick = None
        
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            user_to_kick = reply_msg.sender_id
            
            bot_me = await bot.get_me()
            if user_to_kick == bot_me.id:
                await event.respond("Yeahhh, I'm not going to kick myself.")
                return
        else:
            args = event.message.text.split()[1:]
            if not args:
                await event.respond("❌ Usage: `/kick @username` or `/kick user_id`")
                return
            
            target = args[0]
            if target.startswith('@'):
                user_to_kick = target
            else:
                try:
                    user_to_kick = int(target)
                except ValueError:
                    await event.respond("❌ Invalid user ID!")
                    return
        
        await bot.kick_participant(GROUP_ID, user_to_kick)
        await event.respond(f"👢 User kicked from the group!")
        
    except Exception as e:
        log_error("Kick error", e)
        await event.respond(f"❌ Error: {str(e)}")

# Broadcast
@bot.on(events.NewMessage(pattern='^/broadcast$'))
async def broadcast_handler(event):
    try:
        if not is_admin(event.sender_id):
            await event.respond("❌ Not authorized!")
            return
        
        await event.respond(
            "📢 <b>Broadcast Mode Activated!</b>\n\n"
            "Send the message you want to broadcast.\n\n"
            "Send /cancel to cancel.",
            parse_mode='html'
        )
        
        broadcast_state[event.sender_id] = {'waiting': True}
    except Exception as e:
        log_error("Broadcast init error", e)

@bot.on(events.NewMessage(pattern='^/cancel$'))
async def cancel_handler(event):
    try:
        cancelled = False
        cancel_message = ""
        
        if event.sender_id in broadcast_state:
            del broadcast_state[event.sender_id]
            cancel_message = "❌ Broadcast cancelled."
            cancelled = True
        
        elif event.sender_id in order_states:
            del order_states[event.sender_id]
            cancel_message = "❌ Order cancelled."
            cancelled = True
        
        elif event.sender_id in admin_remark_state:
            del admin_remark_state[event.sender_id]
            cancel_message = "❌ Remark cancelled."
            cancelled = True
        
        elif event.sender_id in ticket_states:
            del ticket_states[event.sender_id]
            cancel_message = "❌ Ticket creation cancelled."
            cancelled = True
        
        elif event.sender_id in raffle_creation_state:
            del raffle_creation_state[event.sender_id]
            cancel_message = "❌ Raffle creation cancelled."
            cancelled = True
        
        elif event.sender_id in deposit_states:
            del deposit_states[event.sender_id]
            cancel_message = "❌ Deposit cancelled."
            cancelled = True
        
        elif event.sender_id in boxing_service_states:
            del boxing_service_states[event.sender_id]
            cancel_message = "❌ Boxing service order cancelled."
            cancelled = True
        
        elif event.sender_id in admin_complete_order_states:
            del admin_complete_order_states[event.sender_id]
            cancel_message = "❌ Order completion cancelled."
            cancelled = True
        
        elif event.sender_id in admin_resources_state:
            del admin_resources_state[event.sender_id]
            cancel_message = "❌ Resources update cancelled."
            cancelled = True
        
        elif event.sender_id in admin_form_state:
            del admin_form_state[event.sender_id]
            cancel_message = "❌ Form update cancelled."
            cancelled = True
        
        elif event.sender_id in admin_service_state:
            del admin_service_state[event.sender_id]
            cancel_message = "❌ Service creation cancelled."
            cancelled = True
        
        elif event.sender_id in admin_reseller_state:
            del admin_reseller_state[event.sender_id]
            cancel_message = "❌ Reseller pricing update cancelled."
            cancelled = True
        
        elif event.sender_id in admin_method_state:
            # If method was being created, delete it
            state = admin_method_state[event.sender_id]
            if state.get('method_id') and state.get('action') == 'add':
                delete_method(state['method_id'])
            del admin_method_state[event.sender_id]
            cancel_message = "❌ Method creation cancelled."
            cancelled = True
        
        if cancelled:
            # Send cancellation message with countdown
            msg = await event.respond(cancel_message)
            
            for i in range(5, 0, -1):
                await asyncio.sleep(1)
                await msg.edit(f"{cancel_message}\n\n⏳ Redirecting to Main Menu in {i} seconds...")
            
            # Redirect to main menu
            await send_main_menu(event.sender_id)
            
    except Exception as e:
        log_error("Cancel error", e)

# End chat/ticket
@bot.on(events.NewMessage(pattern='^/endchat$'))
async def endchat_handler(event):
    try:
        tickets = load_json(tickets_file)
        
        for ticket_id, ticket in tickets.items():
            if ticket['status'] == 'active' and (event.sender_id == ticket['user_id'] or is_admin(event.sender_id)):
                
                ticket['status'] = 'closed'
                ticket['ended_at'] = datetime.now().isoformat()
                save_json(tickets_file, tickets)
                
                transcript_file = f"transcripts/{ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(f"Support Ticket Transcript\n")
                    f.write(f"Ticket ID: {ticket_id}\n")
                    f.write(f"User: {ticket['user_name']} (ID: {ticket['user_id']})\n")
                    f.write(f"Question: {ticket['question']}\n")
                    f.write(f"Started: {ticket['timestamp']}\n")
                    f.write(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    
                    for msg in ticket['messages']:
                        f.write(f"[{msg['timestamp']}] {msg['from'].upper()}: {msg['text']}\n")
                
                await notify_admins(
                    f"💬 <b>Ticket Closed</b>\n\nUser: {ticket['user_name']}\nTicket: {ticket_id}",
                    file=transcript_file
                )
                
                await bot.send_file(
                    ticket['user_id'],
                    transcript_file,
                    caption=f"💬 <b>Support Chat Ended</b>\n\nTicket: {ticket_id}\n<i>Thank you for contacting us!</i>",
                    parse_mode='html'
                )
                
                await event.respond("✅ Chat ended. Transcript sent.")
                return
        
        await event.respond("❌ No active chat found.")
    except Exception as e:
        log_error("End chat error", e)

# Handle order input
async def handle_order_input(event):
    try:
        user_id = event.sender_id
        state = order_states[user_id]
        
        current_field = state['current_field']
        user_input = event.message.text
        
        # Validate order_total is numeric
        if current_field == 'order_total':
            try:
                float(user_input)
            except ValueError:
                await event.respond("❌ <b>Invalid Amount</b>\n\n<i>Please enter a valid number (e.g., 100 or 99.99)</i>", parse_mode='html')
                return
        
        # Validate phone_number is numeric (can include country code)
        if current_field == 'phone_number':
            cleaned = user_input.replace('+', '').replace('-', '').replace(' ', '')
            if not cleaned.isdigit():
                await event.respond("❌ <b>Invalid Phone Number</b>\n\n<i>Please enter a valid phone number (e.g., +1234567890)</i>", parse_mode='html')
                return
        
        state['order_data'][current_field] = user_input
        
        fields = ['first_name', 'last_name', 'order_number', 'order_total', 'login_details', 'mailbox_login', 'delivery_address', 'billing_address', 'track_number', 'phone_number']
        
        current_index = fields.index(current_field)
        
        if current_index < len(fields) - 1:
            next_field = fields[current_index + 1]
            state['current_field'] = next_field
            
            field_prompts = {
                'first_name': '👤 <b>First Name</b>\n<i>Enter your first name:</i>',
                'last_name': '👤 <b>Last Name</b>\n<i>Enter your last name:</i>',
                'order_number': '🔢 <b>Order Number</b>\n<i>Enter the order number:</i>',
                'order_total': '💰 <b>Order Total (USD)</b>\n<i>Enter the total amount (numbers only):</i>',
                'login_details': '🔐 <b>Login Details</b>\n<i>Format: email:password</i>',
                'mailbox_login': '📧 <b>Mailbox Login</b>\n<i>Format: email:password or "N/A"</i>',
                'delivery_address': '🏠 <b>Delivery Address</b>\n<i>Enter full delivery address:</i>',
                'billing_address': '📍 <b>Billing Address</b>\n<i>Enter billing address:</i>',
                'track_number': '📦 <b>Track Number</b>\n<i>Enter tracking number:</i>',
                'phone_number': '📱 <b>Phone Number</b>\n<i>Enter your phone number (numbers only, country code allowed) or or "N/A":</i>'
            }
            
            await event.respond(field_prompts[next_field], parse_mode='html')
        else:
            state['active'] = False
            await show_order_confirmation(event)
    except Exception as e:
        log_error("Order input error", e)

async def show_order_confirmation(event):
    try:
        user_id = event.sender_id
        state = order_states[user_id]
        data = state['order_data']
        store_info = state['store_info']
        
        try:
            order_total = float(data['order_total'])
            # Use new fee format if available, otherwise fall back to old format
            if 'fee' in store_info:
                fee = calculate_fee(order_total, fee_string=store_info['fee'])
                fee_display = store_info['fee']
            else:
                fee = calculate_fee(order_total, store_info.get('fee_percentage', 18), store_info.get('fee_fixed', 0))
                fee_display = f"{store_info.get('fee_percentage', 18)}%"
            # User only pays the fee, not order total + fee
            total_to_pay = fee
        except:
            fee = 0
            total_to_pay = 0
            fee_display = "18%"
        
        message = (
            f"✅ <b>Order Confirmation</b>\n\n"
            f"🏪 <b>Store:</b> {store_info['name']}\n\n"
            f"<b>📋 Customer Details</b>\n"
            f"• Name: {data['first_name']} {data['last_name']}\n"
            f"• Phone: {data['phone_number']}\n\n"
            f"<b>💰 Payment Details</b>\n"
            f"• Order Total: ${data['order_total']}\n"
            f"• Your Fee ({fee_display}): ${fee}\n"
            f"• <b>You Pay: ${total_to_pay}</b>\n\n"
            f"<b>📦 Order Information</b>\n"
            f"• Order #: {data['order_number']}\n"
            f"• Track #: {data['track_number']}\n\n"
            f"<b>🔐 Account Credentials</b>\n"
            f"• Login: {data['login_details']}\n"
            f"• Mailbox: {data['mailbox_login']}\n\n"
            f"<b>📍 Addresses</b>\n"
            f"• Delivery: {data['delivery_address']}\n"
            f"• Billing: {data['billing_address']}\n\n"
            f"⏱ <b>Processing:</b> {store_info.get('timeframe', store_info.get('processing', 'TBD'))}\n"
            f"✅ <b>Success Rate:</b> {store_info['success_rate']}\n\n"
            f"⚠️ <i>Please review carefully before confirming</i>"
        )
        
        buttons = [
            [Button.inline("✅ Confirm Order", b"confirm_order")],
            [Button.inline("❌ Cancel", b"cancel_order"), Button.inline("🏠 Home", b"main_menu")]
        ]
        
        await event.respond(message, buttons=buttons, parse_mode='html')
    except Exception as e:
        log_error("Order confirmation error", e)

# Handle deposit input
async def handle_deposit_input(event):
    try:
        user_id = event.sender_id
        
        if user_id not in deposit_states:
            return
        
        amount_text = event.message.text.strip()
        
        try:
            amount = float(amount_text)
            if amount < 1:
                await event.respond("❌ <b>Invalid Amount</b>\n\n<i>Minimum deposit is $1 USD</i>", parse_mode='html')
                return
            
            # Create payment
            payment_link, payment_id = await create_payment(
                user_id,
                amount,
                f"Wallet Deposit - ${amount} USD"
            )
            
            if payment_link:
                message = format_payment_message(amount, payment_link, payment_id, 120)
                
                buttons = [
                    [Button.url("💳 Pay Now", payment_link)],
                    [Button.inline("🔄 Check Payment Status", f"check_payment_{payment_id}".encode())],
                    [Button.inline("🏠 Main Menu", b"main_menu")]
                ]
                
                msg = await event.respond(message, buttons=buttons, parse_mode='html')
                # Start countdown in background
                asyncio.create_task(show_payment_countdown(msg, user_id, amount, payment_link, payment_id, 'deposit'))
                
                del deposit_states[user_id]
            else:
                await event.respond("❌ <b>Payment Error</b>\n\n<i>Failed to create payment. Please try again later.</i>", parse_mode='html')
                del deposit_states[user_id]
                
        except ValueError:
            await event.respond("❌ <b>Invalid Amount</b>\n\n<i>Please enter a valid number (e.g., 50 or 99.99)</i>", parse_mode='html')
            
    except Exception as e:
        log_error("Deposit input error", e)

# Handle boxing service input
async def handle_boxing_service_input(event):
    try:
        user_id = event.sender_id
        
        if user_id not in boxing_service_states:
            return
        
        state = boxing_service_states[user_id]
        current_field = state.get('current_field')
        
        # RTS + DMG flow (tracking number -> payment)
        if current_field == 'tracking':
            tracking = event.message.text.strip()
            state['order_data']['tracking_number'] = tracking
            state['current_field'] = None
            
            # Show confirmation and proceed to payment
            confirmation = (
                f"✅ <b>Boxing Service Confirmation</b>\n\n"
                f"📦 <b>Service:</b> {state['service_name']}\n"
                f"💰 <b>Price:</b> ${state['price']} USD\n\n"
                f"<b>📋 Order Details:</b>\n"
                f"• Tracking Number: {tracking}\n\n"
                f"<i>Confirm to proceed with payment</i>"
            )
            
            buttons = [
                [Button.inline("✅ Confirm & Pay", f"confirm_boxing_{state['service_key']}".encode())],
                [Button.inline("❌ Cancel", b"cancel_boxing")]
            ]
            
            await event.respond(confirmation, buttons=buttons, parse_mode='html')
        
        # FTID / UPS LIT flow (file -> tracking -> courier -> payment)
        elif current_field == 'file':
            if event.message.media:
                # Download file
                file_path = f"uploads/boxing_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                await event.download_media(file_path)
                state['order_data']['file_path'] = file_path
                state['current_field'] = 'track_number'
                
                await event.respond(
                    "📦 <b>Track Number</b>\n\n"
                    "<i>Please enter the tracking number:</i>",
                    parse_mode='html'
                )
            else:
                await event.respond("❌ <b>File Required</b>\n\n<i>Please upload the return label file</i>", parse_mode='html')
        
        elif current_field == 'track_number':
            state['order_data']['track_number'] = event.message.text
            state['current_field'] = 'courier_service'
            
            await event.respond(
                "🚚 <b>Courier Service</b>\n\n"
                "<i>Please enter the name of the courier service (e.g., UPS, USPS, FedEx):</i>",
                parse_mode='html'
            )
        
        elif current_field == 'courier_service':
            state['order_data']['courier_service'] = event.message.text
            state['current_field'] = None
            
            # Show confirmation
            confirmation = (
                f"✅ <b>Boxing Service Confirmation</b>\n\n"
                f"📦 <b>Service:</b> {state['service_name']}\n"
                f"💰 <b>Price:</b> ${state['price']} USD\n\n"
                f"<b>📋 Order Details:</b>\n"
                f"• Track Number: {state['order_data']['track_number']}\n"
                f"• Courier: {state['order_data']['courier_service']}\n"
                f"• File: Uploaded ✓\n\n"
                f"<i>Confirm to proceed with payment</i>"
            )
            
            buttons = [
                [Button.inline("✅ Confirm & Pay", f"confirm_boxing_{state['service_key']}".encode())],
                [Button.inline("❌ Cancel", b"cancel_boxing")]
            ]
            
            await event.respond(confirmation, buttons=buttons, parse_mode='html')
            
    except Exception as e:
        log_error("Boxing service input error", e)

# Handle ticket input
async def handle_ticket_input(event):
    try:
        user_id = event.sender_id
        
        if user_id not in ticket_states:
            return
        
        state = ticket_states[user_id]
        
        if state.get('waiting_for_question'):
            question = event.message.text
            user_name = state['user_name']
            
            ticket_id = create_ticket(user_id, question, user_name)
            
            try:
                user_entity = await bot.get_entity(user_id)
                user_link = f"<a href='tg://user?id={user_id}'>{user_name}</a>"
                
                admin_notification = (
                    f"🎫 <b>New Support Ticket</b>\n\n"
                    f"👤 User: {user_link}\n"
                    f"🆔 User ID: <code>{user_id}</code>\n"
                    f"🎫 Ticket: <code>{ticket_id}</code>\n\n"
                    f"<b>Question:</b>\n<i>{question}</i>"
                )
                
                admin_buttons = [
                    [Button.inline("✅ Accept", f"accept_ticket_{ticket_id}".encode()),
                     Button.inline("❌ Reject", f"reject_ticket_{ticket_id}".encode())]
                ]
                
                await notify_admins(admin_notification, buttons=admin_buttons)
            except Exception as e:
                log_error(f"Failed to notify admin about ticket", e)
            
            await event.respond(
                f"✅ <b>Ticket Created!</b>\n\n"
                f"🎫 Ticket ID: <code>{ticket_id}</code>\n\n"
                f"⏳ Waiting for admin to accept your request...\n\n"
                f"<i>You'll be notified once an admin responds.</i>",
                parse_mode='html'
            )
            
            del ticket_states[user_id]
    except Exception as e:
        log_error("Ticket input error", e)

# Handle raffle creation input
async def handle_raffle_input(event):
    try:
        user_id = event.sender_id
        
        if not is_admin(user_id) or user_id not in raffle_creation_state:
            return
        
        state = raffle_creation_state[user_id]
        current_field = state.get('current_field')
        
        if current_field == 'prize':
            state['prize'] = event.message.text
            state['current_field'] = 'winners'
            await event.respond(
                "🏆 <b>Number of Winners</b>\n\n"
                "<i>How many winners should this raffle have?</i>",
                parse_mode='html'
            )
        
        elif current_field == 'winners':
            try:
                winners = int(event.message.text)
                if winners <= 0:
                    raise ValueError
                state['winners_count'] = winners
                state['current_field'] = 'duration'
                await event.respond(
                    "⏱ <b>Raffle Duration</b>\n\n"
                    "<i>How long should the raffle run?</i>\n\n"
                    "Format examples:\n"
                    "• 30m (30 minutes)\n"
                    "• 2h (2 hours)\n"
                    "• 1d (1 day)",
                    parse_mode='html'
                )
            except ValueError:
                await event.respond("❌ Please enter a valid number!")
        
        elif current_field == 'duration':
            try:
                duration_text = event.message.text.lower().strip()
                
                if duration_text.endswith('m'):
                    duration_minutes = int(duration_text[:-1])
                elif duration_text.endswith('h'):
                    duration_minutes = int(duration_text[:-1]) * 60
                elif duration_text.endswith('d'):
                    duration_minutes = int(duration_text[:-1]) * 1440
                else:
                    duration_minutes = int(duration_text)
                
                if duration_minutes <= 0:
                    raise ValueError
                
                state['duration_minutes'] = duration_minutes
                state['current_field'] = None
                
                end_time = datetime.now() + timedelta(minutes=duration_minutes)
                
                confirmation = (
                    f"🎁 <b>Raffle Summary</b>\n\n"
                    f"🏆 Prize: {state['prize']}\n"
                    f"👥 Winners: {state['winners_count']}\n"
                    f"⏱ Duration: {duration_minutes} minutes\n"
                    f"⏰ Ends at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"<i>Confirm to create and post the raffle</i>"
                )
                
                buttons = [
                    [Button.inline("✅ Create Raffle", b"create_raffle_confirm")],
                    [Button.inline("❌ Cancel", b"cancel_raffle")]
                ]
                
                await event.respond(confirmation, buttons=buttons, parse_mode='html')
            
            except ValueError:
                await event.respond("❌ Please enter a valid duration! (e.g., 30m, 2h, 1d)")
    
    except Exception as e:
        log_error("Raffle input error", e)

# Handle admin complete order input
async def handle_admin_complete_order(event):
    try:
        user_id = event.sender_id
        
        if not is_admin(user_id) or user_id not in admin_complete_order_states:
            return
        
        state = admin_complete_order_states[user_id]
        order_id = state['order_id']
        
        # Store delivery content
        delivery_content = {
            'type': 'text' if not event.message.media else 'media',
            'content': event.message.text if not event.message.media else None,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Download media if present
        if event.message.media:
            file_path = f"uploads/delivery_{order_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            await event.download_media(file_path)
            delivery_content['file_path'] = file_path
        
        state['delivery_content'] = delivery_content
        
        # Show confirmation
        message = (
            f"✅ <b>Order Delivery Confirmation</b>\n\n"
            f"🆔 Order: <code>{order_id}</code>\n\n"
            f"📦 Content Type: {delivery_content['type'].title()}\n\n"
            f"<i>Click Complete to deliver this order to the customer</i>"
        )
        
        buttons = [
            [Button.inline("✅ Complete Order", f"admin_final_complete_{order_id}".encode())],
            [Button.inline("❌ Cancel", b"admin_cancel_complete")]
        ]
        
        await event.respond(message, buttons=buttons, parse_mode='html')
        
    except Exception as e:
        log_error("Admin complete order input error", e)

# Message handler
@bot.on(events.NewMessage(incoming=True))
async def message_handler(event):
    try:
        user_id = event.sender_id
        
        # Ignore commands
        if event.message.text and event.message.text.startswith('/'):
            return
        
        # Admin resources link update state
        if is_admin(user_id) and user_id in admin_resources_state and event.is_private:
            new_link = event.message.text.strip()
            
            # Basic URL validation
            if new_link.startswith('http://') or new_link.startswith('https://'):
                set_resources_link(new_link)
                await event.respond(
                    f"✅ <b>Resources link updated successfully!</b>\n\n"
                    f"<b>New Link:</b>\n{new_link}",
                    parse_mode='html',
                    buttons=[[Button.inline("🔙 Admin Panel", b"admin_panel")]]
                )
            else:
                await event.respond(
                    "❌ <b>Invalid URL!</b>\n\n"
                    "Please send a valid URL starting with http:// or https://",
                    parse_mode='html'
                )
                return
            
            del admin_resources_state[user_id]
            return
        
        # Admin form link update state
        if is_admin(user_id) and user_id in admin_form_state and event.is_private:
            new_link = event.message.text.strip()
            
            # Basic URL validation
            if new_link.startswith('http://') or new_link.startswith('https://'):
                set_form_link(new_link)
                await event.respond(
                    f"✅ <b>Form link updated successfully!</b>\n\n"
                    f"<b>New Link:</b>\n{new_link}",
                    parse_mode='html',
                    buttons=[[Button.inline("🔙 Admin Panel", b"admin_panel")]]
                )
            else:
                await event.respond(
                    "❌ <b>Invalid URL!</b>\n\n"
                    "Please send a valid URL starting with http:// or https://",
                    parse_mode='html'
                )
                return
            
            del admin_form_state[user_id]
            return
        
        # Admin service creation state
        if is_admin(user_id) and user_id in admin_service_state and event.is_private:
            text = event.message.text.strip()
            state = admin_service_state[user_id]
            
            if state['step'] == 'name':
                # Save name and ask for description
                state['name'] = text
                state['step'] = 'description'
                
                await event.respond(
                    f"➕ <b>Add New Service</b>\n\n"
                    f"✅ Service Name: {text}\n\n"
                    f"📝 <b>Step 2/3:</b> Service Description\n\n"
                    f"Please send the service description:\n"
                    f"<i>(Describe what the service offers)</i>\n\n"
                    f"Type /cancel to abort",
                    parse_mode='html'
                )
                return
            
            elif state['step'] == 'description':
                # Save description and ask for price
                state['description'] = text
                state['step'] = 'price'
                
                await event.respond(
                    f"➕ <b>Add New Service</b>\n\n"
                    f"✅ Service Name: {state['name']}\n"
                    f"✅ Description: {text[:50]}...\n\n"
                    f"📝 <b>Step 3/3:</b> Service Price\n\n"
                    f"Please send the price (in USD):\n"
                    f"<i>(e.g., 50 or 99.99)</i>\n\n"
                    f"Type /cancel to abort",
                    parse_mode='html'
                )
                return
            
            elif state['step'] == 'price':
                # Validate and save price
                try:
                    price = float(text)
                    if price <= 0:
                        raise ValueError("Price must be positive")
                    
                    # Generate service ID
                    service_id = f"custom_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Save service
                    add_custom_service(service_id, state['name'], state['description'], price)
                    
                    await event.respond(
                        f"✅ <b>Service Added Successfully!</b>\n\n"
                        f"📝 <b>Name:</b> {state['name']}\n"
                        f"📄 <b>Description:</b> {state['description']}\n"
                        f"💰 <b>Price:</b> ${price}\n\n"
                        f"<i>Service is now available in 'Other Services' menu!</i>",
                        parse_mode='html',
                        buttons=[[Button.inline("🔙 Admin Panel", b"admin_panel")]]
                    )
                    
                    del admin_service_state[user_id]
                    return
                    
                except ValueError:
                    await event.respond(
                        "❌ <b>Invalid price!</b>\n\n"
                        "Please send a valid number (e.g., 50 or 99.99)",
                        parse_mode='html'
                    )
                    return
        
        # Admin reseller pricing state
        if is_admin(user_id) and user_id in admin_reseller_state and event.is_private:
            text = event.message.text.strip()
            state = admin_reseller_state[user_id]
            
            if state['step'] == 'user_id':
                # Validate user ID
                try:
                    reseller_id = int(text)
                    state['reseller_id'] = reseller_id
                    state['step'] = 'service'
                    
                    await event.respond(
                        f"💰 <b>Set Reseller Pricing</b>\n\n"
                        f"✅ User ID: {reseller_id}\n\n"
                        f"📝 <b>Step 2/3:</b> Service Name\n\n"
                        f"Please send the service name:\n"
                        f"<i>Available services:</i>\n"
                        f"• ftid\n"
                        f"• rts_dmg\n"
                        f"• ups_lit\n\n"
                        f"Type /cancel to abort",
                        parse_mode='html'
                    )
                    return
                except ValueError:
                    await event.respond(
                        "❌ <b>Invalid User ID!</b>\n\n"
                        "Please send a valid numerical user ID",
                        parse_mode='html'
                    )
                    return
            
            elif state['step'] == 'service':
                # Validate service
                service_name = text.lower()
                if service_name not in ['ftid', 'rts_dmg', 'ups_lit']:
                    await event.respond(
                        "❌ <b>Invalid Service!</b>\n\n"
                        "Please choose from: ftid, rts_dmg, ups_lit",
                        parse_mode='html'
                    )
                    return
                
                state['service_name'] = service_name
                state['step'] = 'price'
                
                await event.respond(
                    f"💰 <b>Set Reseller Pricing</b>\n\n"
                    f"✅ User ID: {state['reseller_id']}\n"
                    f"✅ Service: {service_name}\n\n"
                    f"📝 <b>Step 3/3:</b> Custom Price\n\n"
                    f"Please send the custom price (in USD):\n"
                    f"<i>(e.g., 15 or 22.50)</i>\n\n"
                    f"Type /cancel to abort",
                    parse_mode='html'
                )
                return
            
            elif state['step'] == 'price':
                # Validate and save price
                try:
                    price = float(text)
                    if price <= 0:
                        raise ValueError("Price must be positive")
                    
                    # Save reseller pricing
                    set_reseller_pricing(state['reseller_id'], state['service_name'], price)
                    
                    await event.respond(
                        f"✅ <b>Reseller Pricing Set!</b>\n\n"
                        f"👤 <b>User ID:</b> {state['reseller_id']}\n"
                        f"📦 <b>Service:</b> {state['service_name']}\n"
                        f"💰 <b>Custom Price:</b> ${price}\n\n"
                        f"<i>User will now see this pricing!</i>",
                        parse_mode='html',
                        buttons=[[Button.inline("🔙 Admin Panel", b"admin_panel")]]
                    )
                    
                    del admin_reseller_state[user_id]
                    return
                    
                except ValueError:
                    await event.respond(
                        "❌ <b>Invalid price!</b>\n\n"
                        "Please send a valid number (e.g., 15 or 22.50)",
                        parse_mode='html'
                    )
                    return
        
        # Admin remark state
        if is_admin(user_id) and user_id in admin_remark_state and event.is_private:
            order_id = admin_remark_state[user_id]['order_id']
            remark_text = event.message.text
            
            if add_order_remark(order_id, remark_text, by_admin=True):
                order = get_order(order_id)
                customer_id = order['user_id']
                
                await bot.send_message(
                    customer_id,
                    f"📝 <b>New Update on Your Order</b>\n\n"
                    f"🆔 Order: <code>{order_id}</code>\n\n"
                    f"<b>Admin Remark:</b>\n<i>{remark_text}</i>\n\n"
                    f"Check your profile for full details!",
                    parse_mode='html'
                )
                
                await event.respond(f"✅ Remark added to order {order_id}")
            else:
                await event.respond("❌ Failed to add remark")
            
            del admin_remark_state[user_id]
            return
        
        # Admin complete order state
        if is_admin(user_id) and user_id in admin_complete_order_states and event.is_private:
            await handle_admin_complete_order(event)
            return
        
        # Active ticket conversation
        tickets = load_json(tickets_file)
        active_ticket = None
        
        for ticket_id, ticket in tickets.items():
            if ticket['status'] == 'active' and event.is_private:
                if user_id == ticket['user_id'] or is_admin(user_id):
                    active_ticket = ticket_id
                    break
        
        if active_ticket:
            ticket_data = tickets[active_ticket]
            
            add_ticket_message(active_ticket, event.message.text or '[Media]', from_admin=(is_admin(user_id)))
            
            if is_admin(user_id):
                recipient = ticket_data['user_id']
                prefix = "👨‍💼 <b>Admin:</b>\n"
                try:
                    if event.message.media:
                        await bot.send_file(recipient, event.message.media, caption=prefix + (event.message.text or ''), parse_mode='html')
                    else:
                        await bot.send_message(recipient, prefix + event.message.text, parse_mode='html')
                except Exception as e:
                    log_error(f"Ticket message forward error", e)
            else:
                user_name = ticket_data['user_name']
                prefix = f"👤 <b>{user_name}:</b>\n"
                try:
                    if event.message.media:
                        await notify_admins(prefix + (event.message.text or ''), file=event.message.media)
                    else:
                        await notify_admins(prefix + event.message.text)
                except Exception as e:
                    log_error(f"Ticket message forward error", e)
            
            return
        
        # Admin Method State - Handle method creation/editing
        if user_id in admin_method_state and is_admin(user_id):
            state = admin_method_state[user_id]
            
            if state['action'] == 'add' and state['step'] == 'info':
                # Parse method info
                text = event.message.text.strip()
                
                # Try to parse different formats
                method_data = {}
                
                # Try detailed format first (Name: X, Price: Y, etc.)
                if 'name:' in text.lower() or 'price:' in text.lower():
                    for line in text.split('\n'):
                        line = line.strip()
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower()
                            value = value.strip()
                            
                            if key == 'name':
                                method_data['name'] = value
                            elif key == 'price':
                                # Extract number from price
                                price_match = re.search(r'[\d.]+', value)
                                if price_match:
                                    method_data['price'] = float(price_match.group())
                            elif key == 'description':
                                method_data['description'] = value
                            elif key == 'tags':
                                method_data['tags'] = [t.strip() for t in value.split(',')]
                
                # Try simple format (Name Price or Name $Price or Name=Price)
                else:
                    # Match patterns like "PayPal Method 25.99" or "PayPal Method $25.99" or "PayPal Method = 25.99"
                    match = re.search(r'(.+?)[=\s]+\$?([\d.]+)', text)
                    if match:
                        method_data['name'] = match.group(1).strip()
                        method_data['price'] = float(match.group(2))
                
                if 'name' not in method_data or 'price' not in method_data:
                    await event.respond(
                        "❌ <b>Invalid Format!</b>\n\n"
                        "Please use one of these formats:\n\n"
                        "<code>PayPal Method 25.99</code>\n"
                        "<code>Name: PayPal Method, Price: 25.99</code>\n\n"
                        "Try again or send /cancel",
                        parse_mode='html'
                    )
                    return
                
                # Add region to method data
                method_data['region'] = state.get('region', 'Worldwide')
                
                # Create method
                method_id = add_method(method_data)
                state['method_id'] = method_id
                state['step'] = 'files'
                
                region_flags = {
                    'UK': '🇬🇧',
                    'EU': '🇪🇺',
                    'USA': '🇺🇸',
                    'CANADA': '🇨🇦',
                    'Worldwide': '🌐'
                }
                
                tags_display = ', '.join(f'"{t}"' for t in method_data.get('tags', [])) if method_data.get('tags') else 'None'
                
                message = (
                    "✅ <b>Method Created Successfully!</b>\n\n"
                    f"📖 <b>Name:</b> {method_data['name']}\n"
                    f"💰 <b>Price:</b> ${method_data['price']:.2f}\n"
                    f"🌍 <b>Region:</b> {region_flags.get(method_data['region'], '🌐')} {method_data['region']}\n"
                    f"🏷️ <b>Tags:</b> {tags_display}\n"
                    f"📝 <b>Description:</b> {method_data.get('description', 'None')}\n"
                    f"🆔 <b>Method ID:</b> {method_id}\n\n"
                    "<b>Now Upload Files (Optional)</b>\n"
                    "Send files to attach to this method!\n\n"
                    "📄 Send a PDF file for documents\n"
                    "🖼️ Send an image for method preview\n\n"
                    "<i>Or skip if you want to add files later, use Edit Method</i>"
                )
                
                buttons = [
                    [Button.inline("✅ Finish & Broadcast", f"finish_method_{method_id}_broadcast".encode())],
                    [Button.inline("✅ Finish (No Broadcast)", f"finish_method_{method_id}_no".encode())],
                    [Button.inline("❌ Cancel & Delete", f"cancel_method_{method_id}".encode())]
                ]
                
                await event.respond(message, buttons=buttons, parse_mode='html')
                return
            
            elif state['step'] == 'files' and event.message.media:
                method_id = state['method_id']
                method = get_method(method_id)
                
                if not method:
                    await event.respond("❌ Method not found!")
                    del admin_method_state[user_id]
                    return
                
                # Save file
                file_path = f"uploads/method_{method_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                try:
                    downloaded_file = await event.message.download_media(file_path)
                    
                    # Check if it's PDF or image
                    if event.message.document:
                        # PDF
                        update_method(method_id, {'pdf_file': downloaded_file})
                        await event.respond("✅ PDF file attached successfully!")
                    elif event.message.photo:
                        # Image
                        update_method(method_id, {'image_file': downloaded_file})
                        await event.respond("✅ Image attached successfully!")
                    
                    # Show current status
                    method = get_method(method_id)  # Refresh
                    message = (
                        f"📦 <b>Files Attached to {method['name']}</b>\n\n"
                        f"📄 PDF: {'✅ Attached' if method.get('pdf_file') else '❌ Not attached'}\n"
                        f"🖼️ Image: {'✅ Attached' if method.get('image_file') else '❌ Not attached'}\n\n"
                        "<i>Send more files or finish setup</i>"
                    )
                    
                    buttons = [
                        [Button.inline("✅ Finish & Broadcast", f"finish_method_{method_id}_broadcast".encode())],
                        [Button.inline("✅ Finish (No Broadcast)", f"finish_method_{method_id}_no".encode())]
                    ]
                    
                    await event.respond(message, buttons=buttons, parse_mode='html')
                    
                except Exception as e:
                    await event.respond(f"❌ Failed to save file: {str(e)}")
            
            return
        
        # Ticket creation state
        if user_id in ticket_states:
            await handle_ticket_input(event)
            return
        
        # Order creation state
        if user_id in order_states and order_states[user_id].get('active'):
            await handle_order_input(event)
            return
        
        # Deposit state
        if user_id in deposit_states:
            await handle_deposit_input(event)
            return
        
        # Boxing service state
        if user_id in boxing_service_states:
            await handle_boxing_service_input(event)
            return
        
        # Raffle creation state
        if user_id in raffle_creation_state:
            await handle_raffle_input(event)
            return
        
        # Broadcast state
        if user_id in broadcast_state and broadcast_state[user_id].get('waiting'):
            broadcast_state[user_id] = {
                'waiting': False,
                'message': event.message
            }
            
            buttons = [
                [Button.inline("✅ Confirm & Send", b"confirm_broadcast")],
                [Button.inline("❌ Cancel", b"cancel_broadcast")]
            ]
            
            preview = "📢 <b>Broadcast Preview</b>\n\n"
            
            if event.message.media:
                preview += "📎 Type: <b>Media</b>\n"
            else:
                preview += "📝 Type: <b>Text</b>\n"
            
            preview += "\n<i>Click Confirm to broadcast</i>"
            
            await event.respond(preview, buttons=buttons, parse_mode='html')
    
    except Exception as e:
        log_error("Message handler error", e)

# Callback handler - Part 1
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    try:
        data = event.data.decode('utf-8')
        user_id = event.sender_id
        
        # Get user info
        sender = await event.get_sender()
        full_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip()
        user_username = sender.username or "No username"
        
        # Log button click
        await send_log_to_channel(
            "🔘 BUTTON CLICK",
            f"Button: {data}\nUsername: @{user_username}\nFull Name: {full_name}",
            user_id=user_id,
            username=full_name
        )
        
        print(f"[CALLBACK] User {user_id} clicked: {data}")
        
        async def safe_edit(event, message, buttons=None, parse_mode='html'):
            try:
                await event.edit(message, buttons=buttons, parse_mode=parse_mode)
            except Exception as e:
                try:
                    await event.delete()
                except:
                    pass
                try:
                    await bot.send_message(event.chat_id, message, buttons=buttons, parse_mode=parse_mode)
                except Exception as send_error:
                    log_error(f"Failed to send message after edit failed: {send_error}", send_error)
        
        # Browse Hub - Main Menu
        if data == "browse_hub":
            try:
                await event.delete()
            except:
                pass
            
            await send_main_menu(user_id)
        
        # FAQs
        elif data == "faqs":
            faq_message = (
                f"💡 <b>Frequently Asked Questions</b>\n\n"
                
                f"<b>🛍️ What services do we offer?</b>\n"
                f"We specialize in cashback services with an extensive store selection. Plus, we offer:\n"
                f"• Boxing & Replacement services\n"
                f"• Refund Method Store\n"
                f"• ID Verifications\n"
                f"• Carrier Receipts\n"
                f"• Fake PRs & more!\n\n"
                
                f"<b>⚙️ How does it work?</b>\n"
                f"1️⃣ Select a store from our list\n"
                f"2️⃣ Review conditions & choose items\n"
                f"3️⃣ Place your order\n"
                f"4️⃣ Notify us upon delivery\n"
                f"5️⃣ Submit account details via form\n"
                f"6️⃣ We take care of everything else!\n\n"
                f"💡 <i>Some stores offer replacements instead of cashback — resell and earn $10k+/month with minimal effort!</i>\n\n"
                
                f"<b>🏆 Why choose Return?</b>\n"
                f"Return is the name. Excellence is the game.\n"
                f"✅ Never ghosting — always responsive\n"
                f"✅ Professional service guaranteed\n"
                f"✅ We only profit when you do\n"
                f"✅ #1 provider in the industry\n"
                f"✅ Dedicated to maximizing your earnings\n\n"
                
                f"<b>💳 Payment timing & process?</b>\n"
                f"We work first, you pay after confirmation:\n"
                f"• 📧 We send cashback/replacement confirmation\n"
                f"• 💰 You pay our fee after verification\n"
                f"• 🛡️ Middleman service available\n"
                f"• 🏦 Bank transfer option: +5% processing fee\n\n"
                f"⚠️ <i>Can't pay immediately? Let us know beforehand to avoid any consequences.</i>\n\n"
                
                f"<b>🕐 Support availability?</b>\n"
                f"Our team is active 18+ hours daily — we're almost always here to help!\n\n"
                
                f"<b>💰 Accepted payment methods?</b>\n"
                f"• 🪙 Cryptocurrency (all major coins)\n"
                f"• 💳 Revolut (availability may vary)\n"
                f"• 🏦 UK Bank Transfer (availability may vary)\n\n"

                f"<b>⏱️ Processing timeframe?</b>\n"
                f"⏳ Average: 3-5 business days\n"
                f"<i>Timeframes vary by store and are estimates, not guarantees.</i>\n\n"
                
                f"💡 <b>Pro Tip:</b> Always consult us and share your cart before checkout! We customize our methods for each order to ensure success.\n\n"
                
                f"📞 <b>Still have questions?</b> Contact our support team anytime!"
            )
            
            buttons = [[Button.inline("🏠 Back to Menu", b"main_menu")]]
            await safe_edit(event, faq_message, buttons=buttons)
        
        # Support
        elif data == "support":
            support_message = (
                f"💬 <b>Customer Support</b>\n\n"
                f"<i>Choose how you'd like to get help:</i>\n\n"
                f"🆘 <b>Live Chat</b>\n"
                f"Connect with our support team in real-time\n\n"
                f"👨‍💼 <b>Contact Admin</b>\n"
                f"Send a direct message to admin"
            )
            
            buttons = [
                [Button.inline("💬 Start Live Chat", b"start_live_chat")],
                [Button.url("👨‍💼 Contact Admin", "https://t.me/RefundHub_Twink")],
                [Button.inline("🏠 Back to Menu", b"main_menu")]
            ]
            
            await safe_edit(event, support_message, buttons=buttons)
        
        # Start live chat
        elif data == "start_live_chat":
            active = get_active_ticket_for_user(user_id)
            if active:
                await event.answer("⚠️ You already have an active support ticket!", alert=True)
                return
            
            sender = await event.get_sender()
            user_name = sender.first_name or "User"
            
            ticket_states[user_id] = {
                'waiting_for_question': True,
                'user_name': user_name
            }
            
            await safe_edit(
                event,
                f"🎫 <b>Start Live Chat</b>\n\n"
                f"Please describe your issue or question:\n\n"
                f"<i>Type your question below and we'll connect you with support.</i>\n\n"
                f"💡 Send /cancel to abort",
                buttons=None
            )
        
        # Accept ticket
        elif data.startswith("accept_ticket_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            ticket_id = data.replace("accept_ticket_", "")
            ticket = get_ticket(ticket_id)
            
            if ticket and update_ticket(ticket_id, {'status': 'active'}):
                customer_id = ticket['user_id']
                
                await bot.send_message(
                    customer_id,
                    f"✅ <b>Support Chat Started!</b>\n\n"
                    f"🎫 Ticket: <code>{ticket_id}</code>\n\n"
                    f"👨‍💼 An admin has accepted your request.\n"
                    f"💬 You can now chat with support.\n\n"
                    f"<i>Type /endchat to close the conversation</i>",
                    parse_mode='html'
                )
                
                await notify_admins(
                    f"✅ <b>Ticket Accepted</b>\n\n"
                    f"🎫 Ticket: <code>{ticket_id}</code>\n"
                    f"👤 User: {ticket['user_name']}\n\n"
                    f"💬 Chat is now active.\n"
                    f"<i>Type /endchat to close the conversation</i>"
                )
                
                try:
                    await event.edit(
                        (await event.get_message()).message + "\n\n✅ <b>ACCEPTED</b>",
                        buttons=None,
                        parse_mode='html'
                    )
                except:
                    pass
                
                await event.answer("✅ Ticket accepted!", alert=True)
        
        # Reject ticket
        elif data.startswith("reject_ticket_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            ticket_id = data.replace("reject_ticket_", "")
            ticket = get_ticket(ticket_id)
            
            if ticket and update_ticket(ticket_id, {'status': 'rejected'}):
                customer_id = ticket['user_id']
                
                await bot.send_message(
                    customer_id,
                    f"❌ <b>Support Request Rejected</b>\n\n"
                    f"🎫 Ticket: <code>{ticket_id}</code>\n\n"
                    f"<i>Sorry, we're unable to accept your request at this time. Please try again later or contact admin directly.</i>",
                    parse_mode='html'
                )
                
                try:
                    await event.edit(
                        (await event.get_message()).message + "\n\n❌ <b>REJECTED</b>",
                        buttons=None,
                        parse_mode='html'
                    )
                except:
                    pass
                
                await event.answer("❌ Ticket rejected!", alert=True)
        
        # Referral
        elif data == "referral":
            stats = get_referral_stats(user_id)
            user_data = get_user_data(user_id)
            
            bot_username = (await bot.get_me()).username
            referral_link = f"https://t.me/{bot_username}?start={stats['code']}"
            
            referral_message = (
                f"🤝 <b>Your Referral Dashboard</b>\n\n"
                f"<b>📊 Statistics</b>\n"
                f"• Total Referrals: <b>{stats['total']}</b>\n"
                f"• Active Referrals: <b>{stats['active']}</b>\n"
                f"• Referral Code: <code>{stats['code']}</code>\n\n"
                f"<b>🔗 Your Referral Link</b>\n"
                f"<code>{referral_link}</code>\n\n"
                f"<b>💰 Referral Rewards:</b>\n"
                f"💸 Earn <b>25% of every deposit</b> your referrals make!\n"
                f"💳 Rewards are added instantly to your wallet\n\n"
                f"<b>💡 How it works:</b>\n"
                f"1️⃣ Share your referral link with friends\n"
                f"2️⃣ They join using your link\n"
                f"3️⃣ When they deposit, you get <b>25%</b> automatically!\n"
                f"4️⃣ Track your earnings here!\n\n"
                f"🎁 <i>More referrals = More passive income!</i>"
            )
            
            buttons = [
                [Button.inline("📤 Share Link", b"share_referral")],
                [Button.inline("🏠 Back to Menu", b"main_menu")]
            ]
            
            await safe_edit(event, referral_message, buttons=buttons)
        
        # Share referral
        elif data == "share_referral":
            stats = get_referral_stats(user_id)
            bot_username = (await bot.get_me()).username
            referral_link = f"https://t.me/{bot_username}?start={stats['code']}"
            
            share_text = (
                f"🎉 Join Return's Portal - Premium Cashback Services!\n\n"
                f"⚡ 2M+ orders delivered • Trusted since 2023\n"
                f"💰 Earn cashbacks from 60+ premium stores\n"
                f"🚀 Fast processing • Best rates\n\n"
                f"👇 Join now using my referral link:\n"
                f"{referral_link}"
            )
            
            buttons = [
                [Button.switch_inline("📤 Share in Chat", share_text)],
                [Button.inline("🔙 Back", b"referral")],
                [Button.inline("🏠 Back to Menu", b"main_menu")]
            ]
            
            await safe_edit(
                event,
                f"📤 <b>Share Your Referral Link</b>\n\n"
                f"<i>Click the button below to share your referral link in any chat!</i>\n\n"
                f"<code>{referral_link}</code>\n\n"
                f"<i>Or copy the link above and share manually.</i>",
                buttons=buttons
            )
        
        # Games
        elif data == "games":
            await event.answer("🎮 API not set up yet! Coming soon...", alert=True)
        
        # Raffles
        elif data == "raffles":
            active_raffles = get_active_raffles()
            
            if not active_raffles:
                await event.answer("🎁 No active raffles at the moment. Check back later!", alert=True)
                return
            
            message = f"🎁 <b>Active Raffles</b>\n\n<i>Click on a raffle to join:</i>\n\n"
            
            buttons = []
            for raffle_id in active_raffles:
                raffle = get_raffle(raffle_id)
                if raffle:
                    end_time = datetime.fromisoformat(raffle['end_time'])
                    time_left = end_time - datetime.now()
                    hours = int(time_left.total_seconds() // 3600)
                    minutes = int((time_left.total_seconds() % 3600) // 60)
                    
                    raffle_text = f"🎁 {raffle['prize']} ({hours}h {minutes}m left)"
                    buttons.append([Button.inline(raffle_text, f"join_raffle_{raffle_id}".encode())])
            
            buttons.append([Button.inline("🏠 Back to Menu", b"main_menu")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # Join raffle
        elif data.startswith("join_raffle_"):
            raffle_id = data.replace("join_raffle_", "")
            raffle = get_raffle(raffle_id)
            
            if not raffle:
                await event.answer("❌ Raffle not found!", alert=True)
                return
            
            if raffle['status'] != 'active':
                await event.answer("❌ This raffle has ended!", alert=True)
                return
            
            if join_raffle(raffle_id, user_id):
                await event.answer("✅ You've joined the raffle! Good luck!", alert=True)
            else:
                await event.answer("⚠️ You're already in this raffle!", alert=True)
        
        # Other Services
        elif data == "other_services":
            # Get custom services
            custom_services = get_custom_services()
            
            message = (
                f"✨ <b>Other Premium Services</b>\n\n"
                f"<i>Explore our exclusive offerings:</i>\n\n"
                f"🌟 <b>Private Monthly Group</b>\n"
                f"<i>Join exclusive community with insider tips</i>\n\n"
                f"📦 <b>Boxing Service</b>\n"
                f"<i>Professional package handling services</i>"
            )
            
            # Add custom services to message
            if custom_services:
                message += "\n\n<b>━━━ Custom Services ━━━</b>\n"
                for service_id, service in custom_services.items():
                    message += f"\n✨ <b>{service['name']}</b>\n<i>{service['description'][:60]}...</i>\n"
            
            buttons = [
                [Button.inline("🌟 Private Monthly Group", b"private_monthly_group")],
                [Button.inline("📦 Boxing Service", b"boxing_service")]
            ]
            
            # Add custom service buttons
            for service_id, service in custom_services.items():
                buttons.append([Button.inline(f"✨ {service['name']}", f"custom_service_{service_id}".encode())])
            
            buttons.append([Button.inline("🏠 Back to Menu", b"main_menu")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # Custom Service View
        elif data.startswith("custom_service_"):
            service_id = data.replace("custom_service_", "")
            custom_services = get_custom_services()
            
            if service_id in custom_services:
                service = custom_services[service_id]
                
                message = (
                    f"✨ <b>{service['name']}</b>\n\n"
                    f"📄 <b>Description:</b>\n"
                    f"{service['description']}\n\n"
                    f"💰 <b>Price:</b> ${service['price']}\n\n"
                    f"⚡ <i>Secure payment via OxaPay</i>"
                )
                
                buttons = [
                    [Button.inline(f"💳 Purchase - ${service['price']}", f"purchase_custom_{service_id}".encode())],
                    [Button.inline("🔙 Back", b"other_services")],
                    [Button.inline("🏠 Main Menu", b"main_menu")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
            else:
                await event.answer("❌ Service not found!", alert=True)
        
        # Purchase Custom Service
        elif data.startswith("purchase_custom_"):
            service_id = data.replace("purchase_custom_", "")
            custom_services = get_custom_services()
            
            if service_id in custom_services:
                service = custom_services[service_id]
                
                payment_link, payment_id = await create_payment(
                    user_id,
                    service['price'],
                    service['name'],
                    f"CUSTOM-{service_id}-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
                
                if payment_link:
                    message = (
                        f"💳 <b>{service['name']} - Payment</b>\n\n"
                        f"💰 <b>Amount:</b> ${service['price']}\n\n"
                        f"<b>📝 Instructions:</b>\n"
                        f"1. Click the payment button below\n"
                        f"2. Complete payment on OxaPay\n"
                        f"3. Service will be delivered after confirmation\n\n"
                        f"⚠️ <i>Payment expires in 30 minutes</i>"
                    )
                    
                    buttons = [
                        [Button.url("💳 Pay Now", payment_link)],
                        [Button.inline("🔙 Back", f"custom_service_{service_id}".encode())],
                        [Button.inline("🏠 Main Menu", b"main_menu")]
                    ]
                    
                    await safe_edit(event, message, buttons=buttons)
                else:
                    await event.answer("❌ Payment creation failed", alert=True)
            else:
                await event.answer("❌ Service not found!", alert=True)
        
        # Private Monthly Group
        elif data == "private_monthly_group":
            message = (
                f"🌟 <b>Return's Monthly Profit Group</b> 🌟\n\n"
                f"🚫 <b>Tired of:</b>\n"
                f"• Useless chats\n"
                f"• High fees\n"
                f"• Slow progress\n\n"
                f"🔑 <b>Unlock:</b>\n"
                f"• $10,000+ monthly earnings\n"
                f"• Insider store access & exclusive guides\n"
                f"• Trusted cashouts & best resale rates\n"
                f"• Reduced fees for our services\n"
                f"• Private guides and manuals\n"
                f"• Notes from Return\n"
                f"• Personal support from Return\n"
                f"• Community with more than 75+ people in\n"
                f"• ROS/ROD stores\n"
                f"• 75+ stores with methods included\n"
                f"• Discounts on all my services\n\n"
                f"💰 <b>Pricing:</b>\n"
                f"• 75$ per month\n\n"
                f"<i>Click below to purchase access:</i>"
            )
            
            buttons = [
                [Button.inline("💳 Purchase - $75", b"purchase_monthly_group")],
                [Button.inline("🔙 Back", b"other_services")],
                [Button.inline("🏠 Main Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Purchase Monthly Group
        elif data == "purchase_monthly_group":
            payment_link, payment_id = await create_payment(
                user_id,
                75,
                "Private Monthly Group - Monthly Access",
                f"MONTHLY-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            if payment_link:
                message = (
                    f"💳 <b>Private Monthly Group - Payment</b>\n\n"
                    f"💵 Amount: <b>$75.00 USD</b>\n"
                    f"📦 Service: Monthly Access\n\n"
                    f"<b>Payment Instructions:</b>\n"
                    f"1️⃣ Click the payment link below\n"
                    f"2️⃣ Complete the cryptocurrency payment\n"
                    f"3️⃣ Access will be granted automatically\n\n"
                    f"🔐 <i>Secure payment via OxaPay</i>\n"
                    f"⏱ <i>Payment expires in 30 minutes</i>\n\n"
                    f"🆔 Payment ID: <code>{payment_id}</code>"
                )
                
                buttons = [
                    [Button.url("💳 Pay Now", payment_link)],
                    [Button.inline("🔄 Check Status", f"check_payment_{payment_id}".encode())],
                    [Button.inline("🏠 Main Menu", b"main_menu")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
            else:
                await event.answer("❌ Payment error. Please try again.", alert=True)
        
        # Refunding Methods
        elif data == "refunding_methods":
            await event.answer("📚 Coming soon! Stay tuned for exclusive refunding methods.", alert=True)
        
        # Aged Accounts
        elif data == "aged_accounts":
            message = (
                f"👤 <b>Premium Aged Accounts</b>\n\n"
                f"<i>Choose an account type:</i>\n\n"
                f"🍎 <b>Amazon Account</b>\n"
                f"• Well-aged with history\n"
                f"• Ready to use\n"
                f"• Price: $40\n\n"
                f"🍏 <b>Apple Account</b>\n"
                f"• Premium aged account\n"
                f"• Full access\n"
                f"• Price: $55"
            )
            
            buttons = [
                [Button.inline("🍎 Amazon - $40", b"aged_amazon")],
                [Button.inline("🍏 Apple - $55", b"aged_apple")],
                [Button.inline("🔙 Back", b"other_services")],
                [Button.inline("🏠 Main Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        # Aged Amazon Account
        elif data == "aged_amazon":
            payment_link, payment_id = await create_payment(
                user_id,
                40,
                "Aged Amazon Account",
                f"AMAZON-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            if payment_link:
                # Create service order
                order_id = create_service_order(
                    user_id,
                    "aged_account",
                    "Amazon Account",
                    40,
                    {'account_type': 'Amazon', 'payment_id': payment_id}
                )
                
                # Update payment with order reference
                payments = load_json(payments_file)
                if payment_id in payments:
                    payments[payment_id]['service_order_id'] = order_id
                    save_json(payments_file, payments)
                
                message = (
                    f"💳 <b>Aged Amazon Account - Payment</b>\n\n"
                    f"💵 Amount: <b>$40.00 USD</b>\n"
                    f"📦 Service: Premium Aged Amazon Account\n"
                    f"🆔 Order: <code>{order_id}</code>\n\n"
                    f"<b>Payment Instructions:</b>\n"
                    f"1️⃣ Click the payment link below\n"
                    f"2️⃣ Complete the cryptocurrency payment\n"
                    f"3️⃣ Order will be processed automatically\n\n"
                    f"🔐 <i>Secure payment via OxaPay</i>\n"
                    f"⏱ <i>Payment expires in 30 minutes</i>\n\n"
                    f"🆔 Payment ID: <code>{payment_id}</code>"
                )
                
                buttons = [
                    [Button.url("💳 Pay Now", payment_link)],
                    [Button.inline("🔄 Check Status", f"check_payment_{payment_id}".encode())],
                    [Button.inline("🏠 Main Menu", b"main_menu")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
            else:
                await event.answer("❌ Payment error. Please try again.", alert=True)
        
        # Aged Apple Account
        elif data == "aged_apple":
            payment_link, payment_id = await create_payment(
                user_id,
                55,
                "Aged Apple Account",
                f"APPLE-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            if payment_link:
                # Create service order
                order_id = create_service_order(
                    user_id,
                    "aged_account",
                    "Apple Account",
                    55,
                    {'account_type': 'Apple', 'payment_id': payment_id}
                )
                
                # Update payment with order reference
                payments = load_json(payments_file)
                if payment_id in payments:
                    payments[payment_id]['service_order_id'] = order_id
                    save_json(payments_file, payments)
                
                message = (
                    f"💳 <b>Aged Apple Account - Payment</b>\n\n"
                    f"💵 Amount: <b>$55.00 USD</b>\n"
                    f"📦 Service: Premium Aged Apple Account\n"
                    f"🆔 Order: <code>{order_id}</code>\n\n"
                    f"<b>Payment Instructions:</b>\n"
                    f"1️⃣ Click the payment link below\n"
                    f"2️⃣ Complete the cryptocurrency payment\n"
                    f"3️⃣ Order will be processed automatically\n\n"
                    f"🔐 <i>Secure payment via OxaPay</i>\n"
                    f"⏱ <i>Payment expires in 30 minutes</i>\n\n"
                    f"🆔 Payment ID: <code>{payment_id}</code>"
                )
                
                buttons = [
                    [Button.url("💳 Pay Now", payment_link)],
                    [Button.inline("🔄 Check Status", f"check_payment_{payment_id}".encode())],
                    [Button.inline("🏠 Main Menu", b"main_menu")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
            else:
                await event.answer("❌ Payment error. Please try again.", alert=True)
        
        # Boxing Service
        elif data == "boxing_service":
            # Get user-specific pricing
            ftid_price = get_user_price(user_id, 'ftid', 18)
            rts_dmg_price = get_user_price(user_id, 'rts_dmg', 40)
            ups_lit_price = get_user_price(user_id, 'ups_lit', 27)
            
            message = (
                f"📦 <b>Professional Boxing Services</b>\n\n"
                f"<i>Select a service:</i>\n\n"
                f"📦 <b>FTID - UPS/USPS/FEDEX</b> - ${ftid_price}\n"
                f"<i>Fake Tracking ID service</i>\n\n"
                f"📮 <b>RTS + DMG Left with Sender</b> - ${rts_dmg_price}\n"
                f"<i>Return to sender with damage</i>\n\n"
                f"🎨 <b>UPS LIT</b> - ${ups_lit_price}\n"
                f"<i>UPS Label In Transit service</i>"
            )
            
            buttons = [
                [Button.inline(f"📦 FTID - ${ftid_price}", b"boxing_ftid")],
                [Button.inline(f"📮 RTS + DMG - ${rts_dmg_price}", b"boxing_rts_dmg")],
                [Button.inline(f"🎨 UPS LIT - ${ups_lit_price}", b"boxing_ups_lit")],
                [Button.inline("🔙 Back", b"other_services")],
                [Button.inline("🏠 Main Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Boxing service - POD Delete (redirect)
        elif data == "boxing_pod_delete":
            await event.answer("📞 Please contact admin directly for POD Delete service", alert=True)
            buttons = [
                [Button.url("👨‍💼 Contact Admin", "https://t.me/RefundHub_Twink")],
                [Button.inline("🔙 Back", b"boxing_service")],
                [Button.inline("🏠 Main Menu", b"main_menu")]
            ]
            
            message = (
                f"🗑️ <b>POD Delete Service</b>\n\n"
                f"<i>This service requires direct admin contact.</i>\n\n"
                f"📞 Please click below to contact admin:"
            )
            
            await safe_edit(event, message, buttons=buttons)
        
        # Boxing service - UPS Instant (redirect)
        elif data == "boxing_ups_instant":
            await event.answer("📞 Please contact admin directly for UPS Instant AP service", alert=True)
            buttons = [
                [Button.url("👨‍💼 Contact Admin", "https://t.me/RefundHub_Twink")],
                [Button.inline("🔙 Back", b"boxing_service")],
                [Button.inline("🏠 Main Menu", b"main_menu")]
            ]
            
            message = (
                f"⚡ <b>UPS Instant AP - 24/7</b>\n\n"
                f"<i>This service requires direct admin contact.</i>\n\n"
                f"📞 Please click below to contact admin:"
            )
            
            await safe_edit(event, message, buttons=buttons)
        
        # Boxing services that require form
        elif data.startswith("boxing_"):
            service_key = data.replace("boxing_", "")
            
            if service_key in BOXING_SERVICES:
                service_info = BOXING_SERVICES[service_key]
                
                # Get user-specific price
                user_price = get_user_price(user_id, service_key, service_info['price'])
                
                # RTS + DMG has different flow (asks for tracking number)
                if service_info.get('requires_tracking'):
                    boxing_service_states[user_id] = {
                        'service_key': service_key,
                        'service_name': service_info['name'],
                        'price': user_price,
                        'current_field': 'tracking',
                        'order_data': {}
                    }
                    
                    message = (
                        f"📮 <b>{service_info['name']}</b>\n\n"
                        f"💰 Price: <b>${user_price} USD</b>\n\n"
                        f"{service_info.get('note', '')}\n\n"
                        f"<b>📋 Step 1: Tracking Number</b>\n\n"
                        f"<i>Please enter the tracking number below</i>\n"
                        f"⚠️ <i>Only delivered trackings are accepted!</i>\n\n"
                        f"💡 Send /cancel to abort anytime"
                    )
                    
                    buttons = [[Button.inline("❌ Cancel", b"cancel_boxing")]]
                    
                    await safe_edit(event, message, buttons=buttons)
                
                # FTID and UPS LIT ask for file upload
                elif service_info.get('requires_form'):
                    boxing_service_states[user_id] = {
                        'service_key': service_key,
                        'service_name': service_info['name'],
                        'price': user_price,
                        'current_field': 'file',
                        'order_data': {}
                    }
                    
                    message = (
                        f"📦 <b>{service_info['name']}</b>\n\n"
                        f"💰 Price: <b>${user_price} USD</b>\n\n"
                        f"{service_info.get('note', '')}\n\n"
                        f"<b>📋 Step 1: Upload Label File</b>\n\n"
                        f"<i>Please upload the return label file</i>\n\n"
                        f"💡 Send /cancel to abort anytime"
                    )
                    
                    buttons = [[Button.inline("❌ Cancel", b"cancel_boxing")]]
                    
                    await safe_edit(event, message, buttons=buttons)
        
        # Cancel boxing service
        elif data == "cancel_boxing":
            if user_id in boxing_service_states:
                del boxing_service_states[user_id]
            
            await event.answer("❌ Boxing service order cancelled", alert=False)
            await safe_edit(
                event,
                "❌ <b>Order Cancelled</b>\n\n<i>No charges were made.</i>",
                buttons=[[Button.inline("📦 Boxing Service", b"boxing_service"), Button.inline("🏠 Home", b"main_menu")]]
            )
        
        # Confirm boxing service
        elif data.startswith("confirm_boxing_"):
            service_key = data.replace("confirm_boxing_", "")
            
            if user_id not in boxing_service_states:
                await event.answer("❌ Session expired", alert=True)
                return
            
            state = boxing_service_states[user_id]
            
            # Create payment using user-specific price from state
            payment_link, payment_id = await create_payment(
                user_id,
                state['price'],
                f"Boxing Service - {state['service_name']}",
                f"BOX-{service_key.upper()}-{user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            if payment_link:
                # Create service order
                order_id = create_service_order(
                    user_id,
                    "boxing_service",
                    state['service_name'],
                    state['price'],
                    {
                        'service_key': service_key,
                        'track_number': state['order_data'].get('track_number'),
                        'courier_service': state['order_data'].get('courier_service'),
                        'tracking_number': state['order_data'].get('tracking_number'),
                        'file_path': state['order_data'].get('file_path'),
                        'payment_id': payment_id
                    }
                )
                
                # Update payment with order reference
                payments = load_json(payments_file)
                if payment_id in payments:
                    payments[payment_id]['service_order_id'] = order_id
                    save_json(payments_file, payments)
                
                # Build order details display
                order_details = ""
                if state['order_data'].get('tracking_number'):
                    order_details = f"• Tracking #: {state['order_data']['tracking_number']}\n"
                else:
                    order_details = f"• Track #: {state['order_data'].get('track_number', 'N/A')}\n"
                    if state['order_data'].get('courier_service'):
                        order_details += f"• Courier: {state['order_data']['courier_service']}\n"
                    if state['order_data'].get('file_path'):
                        order_details += f"• File: Uploaded ✓\n"
                
                message = (
                    f"💳 <b>Boxing Service - Payment</b>\n\n"
                    f"📦 Service: {state['service_name']}\n"
                    f"💵 Amount: <b>${state['price']:.2f} USD</b>\n"
                    f"🆔 Order: <code>{order_id}</code>\n\n"
                    f"<b>Order Details:</b>\n"
                    f"{order_details}\n"
                    f"<b>Payment Instructions:</b>\n"
                    f"1️⃣ Click the payment link below\n"
                    f"2️⃣ Complete the cryptocurrency payment\n"
                    f"3️⃣ Order will be processed automatically\n\n"
                    f"🔐 <i>Secure payment via OxaPay</i>\n"
                    f"⏱ <i>Payment expires in 30 minutes</i>\n\n"
                    f"🆔 Payment ID: <code>{payment_id}</code>"
                )
                
                buttons = [
                    [Button.url("💳 Pay Now", payment_link)],
                    [Button.inline("🔄 Check Status", f"check_payment_{payment_id}".encode())],
                    [Button.inline("🏠 Main Menu", b"main_menu")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
                
                del boxing_service_states[user_id]
            else:
                await event.answer("❌ Payment error. Please try again.", alert=True)
        
        # Check payment status
        elif data.startswith("check_payment_"):
            payment_id = data.replace("check_payment_", "")
            
            status = await check_payment_status(payment_id)
            
            if status == 'completed':
                payments = load_json(payments_file)
                payment_data = payments.get(payment_id)
                
                if payment_data:
                    # Check if payment was already processed to prevent double-crediting
                    if payment_data.get('processed'):
                        await event.answer("✅ Payment already processed!", alert=True)
                        return
                    
                    amount = payment_data['amount']
                    description = payment_data['description']
                    
                    # Check if it's a wallet deposit
                    if 'Wallet Deposit' in description:
                        # Add to wallet
                        if add_to_wallet(user_id, amount, description):
                            # Mark payment as processed
                            payment_data['processed'] = True
                            payment_data['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            payments[payment_id] = payment_data
                            save_json(payments_file, payments)
                            await event.answer(f"✅ Payment completed! ${amount} added to wallet", alert=True)
                            
                            # Log wallet deposit to logs channel
                            user_entity = await bot.get_entity(user_id)
                            user_name = f"{user_entity.first_name or ''} {user_entity.last_name or ''}".strip()
                            user_username = user_entity.username or "No username"
                            await send_log_to_channel(
                                "💰 WALLET DEPOSIT",
                                f"Wallet Deposit Payment\nAmount: ${amount} USD\nPayment ID: {payment_id}\nUsername: @{user_username}",
                                user_id=user_id,
                                username=user_name
                            )
                            
                            # Process referral reward
                            try:
                                reward_amount = await process_referral_reward(user_id, amount)
                                if reward_amount:
                                    log_error(f"Referral reward processed: ${reward_amount} for user deposit ${amount}", None)
                            except Exception as e:
                                log_error("Failed to process referral reward", e)
                            
                            # Notify admin
                            try:
                                user_entity = await bot.get_entity(user_id)
                                user_name = user_entity.first_name or "User"
                                
                                await bot.send_message(
                                    PAYMENT_NOTIFICATION_CHANNEL,
                                    f"💰 <b>Deposit Received</b>\n\n"
                                    f"👤 User: {user_name} (<code>{user_id}</code>)\n"
                                    f"💵 Amount: ${amount} USD\n"
                                    f"📝 Type: Wallet Deposit\n"
                                    f"🆔 Payment: <code>{payment_id}</code>",
                                    parse_mode='html'
                                )
                            except Exception as e:
                                log_error("Failed to notify admin about deposit", e)
                    
                    # Check if it's a service order
                    elif payment_data.get('service_order_id'):
                        order_id = payment_data['service_order_id']
                        
                        # Update service order status
                        if update_service_order(order_id, {'payment_status': 'paid'}):
                            # Mark payment as processed
                            payment_data['processed'] = True
                            payment_data['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            payments[payment_id] = payment_data
                            save_json(payments_file, payments)
                            
                            service_order = get_service_order(order_id)
                            
                            await event.answer("✅ Payment completed! Order is being processed", alert=True)
                            
                            # Log payment to logs channel
                            user_entity = await bot.get_entity(user_id)
                            user_name = f"{user_entity.first_name or ''} {user_entity.last_name or ''}".strip()
                            user_username = user_entity.username or "No username"
                            await send_log_to_channel(
                                "💰 PAYMENT SUCCESS",
                                f"Service Order Payment\nOrder ID: {order_id}\nService: {service_order['service_name']}\nAmount: ${service_order['price']} USD\nPayment ID: {payment_id}\nUsername: @{user_username}",
                                user_id=user_id,
                                username=user_name
                            )
                            
                            # Notify user
                            await bot.send_message(
                                user_id,
                                f"✅ <b>Payment Successful!</b>\n\n"
                                f"🆔 Order: <code>{order_id}</code>\n"
                                f"📦 Service: {service_order['service_name']}\n"
                                f"💰 Amount: ${service_order['price']} USD\n\n"
                                f"⏳ <b>Your order is being processed</b>\n\n"
                                f"<i>You'll be notified once it's ready for delivery!</i>",
                                parse_mode='html'
                            )
                            
                            # Notify admin
                            try:
                                user_entity = await bot.get_entity(user_id)
                                user_name = user_entity.first_name or "User"
                                
                                admin_message = (
                                    f"🔔 <b>SERVICE ORDER PAID</b>\n\n"
                                    f"🆔 Order: <code>{order_id}</code>\n"
                                    f"👤 User: {user_name} (<code>{user_id}</code>)\n"
                                    f"📦 Service: {service_order['service_name']}\n"
                                    f"💰 Amount: ${service_order['price']} USD\n"
                                    f"💳 Payment: <code>{payment_id}</code>\n\n"
                                    f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                )
                                
                                admin_buttons = [
                                    [Button.inline("✅ Complete Order", f"complete_service_{order_id}".encode())],
                                    [Button.inline("💬 Start Chat", f"start_chat_service_{order_id}".encode())],
                                    [Button.inline("❌ Reject", f"reject_service_{order_id}".encode())]
                                ]
                                
                                await bot.send_message(
                                    ORDERS_CHANNEL_ID,
                                    admin_message,
                                    buttons=admin_buttons,
                                    parse_mode='html'
                                )
                            except Exception as e:
                                log_error("Failed to notify admin about service order", e)
                
                # Update message
                await safe_edit(
                    event,
                    "✅ <b>Payment Completed!</b>\n\n<i>Thank you for your payment. Processing your order...</i>",
                    buttons=[[Button.inline("🏠 Main Menu", b"main_menu")]]
                )
            
            elif status == 'failed':
                await event.answer("❌ Payment expired or failed", alert=True)
            else:
                await event.answer("⏳ Payment is still pending", alert=False)

# Store list - Region Selection
        elif data == "store_list":
            message = (
                f"🌍 <b>Select Your Region</b>\n\n"
                f"<i>Choose your region to browse available stores:</i>\n\n"
                f"🇺🇸 <b>United States</b>\n"
                f"<i>Premium US stores with fast delivery</i>\n\n"
                f"🇬🇧 <b>United Kingdom</b>\n"
                f"<i>Top UK brands and retailers</i>\n\n"
                f"🇪🇺 <b>European Union</b>\n"
                f"<i>EU stores with wide coverage</i>\n\n"
                f"🇨🇦 <b>Canada</b>\n"
                f"<i>Canadian stores and services</i>\n\n"
                f"⚡ <i>All stores verified • Fast processing • Secure</i>"
            )
            
            buttons = [
                [Button.inline("🇺🇸 United States", b"region_USA")],
                [Button.inline("🇬🇧 United Kingdom", b"region_UK")],
                [Button.inline("🇪🇺 European Union", b"region_EU")],
                [Button.inline("🇨🇦 Canada", b"region_CA")],
                [Button.inline("🏠 Back to Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Region Selection - Show Categories
        elif data.startswith("region_"):
            region = data.replace("region_", "")
            if region in STORES:
                region_data = STORES[region]
                categories = region_data['categories']
                
                message = (
                    f"{region_data['flag']} <b>{region_data['name']}</b>\n\n"
                    f"<i>Choose a category to browse stores:</i>\n\n"
                )
                
                buttons = []
                for cat_id, cat_data in categories.items():
                    store_count = len(cat_data['stores'])
                    message += f"{cat_data['name']}\n<i>{store_count} stores available</i>\n\n"
                    buttons.append([Button.inline(cat_data['name'], f"cat_{region}_{cat_id}".encode())])
                
                message += f"⚡ <i>All stores verified • Fast processing • Secure</i>"
                
                buttons.append([Button.inline("🔙 Regions", b"store_list"), Button.inline("🏠 Home", b"main_menu")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # Full Store List - Generate temporary invite link
        elif data == "full_store_list":
            try:
                from telethon.tl.functions.messages import ExportChatInviteRequest
                
                # Generate invite link that expires in 60 seconds
                invite = await bot(ExportChatInviteRequest(
                    peer=-1002919289402,
                    expire_date=int((datetime.now() + timedelta(seconds=60)).timestamp()),
                    usage_limit=1
                ))
                
                # Schedule auto-revoke after 60 seconds
                asyncio.create_task(revoke_invite_links(
                    {'store_list': {'link': invite.link, 'channel_id': -1002919289402}}, 
                    60
                ))
                
                message = (
                    f"📋 <b>Full Store List Access</b>\n\n"
                    f"🔗 Your temporary access link:\n"
                    f"{invite.link}\n\n"
                    f"⏱️ <b>Expires in 60 seconds</b>\n"
                    f"⚠️ <i>Click the link quickly to access our complete store list!</i>"
                )
                
                buttons = [[Button.inline("🏠 Back to Menu", b"main_menu")]]
                await safe_edit(event, message, buttons=buttons)
                
            except Exception as e:
                error_message = (
                    f"❌ <b>Error generating store list link</b>\n\n"
                    f"<i>Please contact support or try again later.</i>"
                )
                buttons = [[Button.inline("🏠 Back to Menu", b"main_menu")]]
                await safe_edit(event, error_message, buttons=buttons)
        
        # Category view - Show stores in category
        elif data.startswith("cat_"):
            parts = data.replace("cat_", "").split("_", 1)
            region = parts[0]
            category = parts[1]
            
            if region in STORES and category in STORES[region]['categories']:
                stores = STORES[region]['categories'][category]['stores']
                category_name = STORES[region]['categories'][category]['name']
                region_flag = STORES[region]['flag']
                
                message = f"{region_flag} {category_name}\n\n<i>Select a store to view details:</i>\n\n"
                
                for store_id, store in stores.items():
                    message += (
                        f"{store['name']}\n"
                        f"<i>💰 Fee: {store['fee']} • "
                        f"Limit: {store['limit']} • "
                        f"⏱️ {store['timeframe']}</i>\n\n"
                    )
                
                message += f"✨ <i>Total: {len(stores)} stores</i>"
                
                buttons = []
                for store_id, store in stores.items():
                    buttons.append([Button.inline(store['name'], f"store_{region}_{category}_{store_id}".encode())])
                
                buttons.append([Button.inline("🔙 Categories", f"region_{region}".encode()), Button.inline("🏠 Home", b"main_menu")])
                
                await safe_edit(event, message, buttons=buttons)
        
        # Store details
        elif data.startswith("store_"):
            parts = data.split("_", 3)  # Split into max 4 parts: ["store", "region", "category", "store_id"]
            if len(parts) >= 4:
                region = parts[1]
                category = parts[2]
                store_id = parts[3]
            else:
                await event.answer("❌ Invalid store selection", alert=True)
                return
            
            if region in STORES and category in STORES[region]['categories'] and store_id in STORES[region]['categories'][category]['stores']:
                store = STORES[region]['categories'][category]['stores'][store_id]
                region_flag = STORES[region]['flag']
                
                message = (
                    f"{region_flag} {store['name']}\n\n"
                    f"<b>📋 Store Information</b>\n\n"
                    f"<b>💰 Fee:</b> {store['fee']}\n"
                    f"<b>📊 Limit:</b> {store['limit']}\n"
                    f"<b>📦 Items:</b> {store['items']}\n"
                    f"<b>⏱️ Timeframe:</b> {store['timeframe']}\n"
                    f"<b>🌍 Region:</b> {store['region']}\n"
                    f"<b>✅ Success Rate:</b> {store['success_rate']}\n\n"
                    f"<b>📝 Description</b>\n"
                    f"{store['description']}\n\n"
                )
                
                if store['notes']:
                    message += f"💡 <i>{store['notes']}</i>\n\n"
                
                message += f"⚡ <i>Trusted • Secure • Fast</i>"
                
                form_link = get_form_link()
                
                buttons = [
                    [Button.inline("🛒 Place Order", f"order_{region}_{category}_{store_id}".encode())],
                    [Button.url("📝 Fill the form", form_link)],
                    [Button.inline("🔙 Back", f"cat_{region}_{category}".encode()), Button.inline("🏠 Home", b"main_menu")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
        
        # Start order
        elif data.startswith("order_"):
            parts = data.split("_", 3)  # Split into max 4 parts: ["order", "region", "category", "store_id"]
            if len(parts) >= 4:
                region = parts[1]
                category = parts[2]
                store_id = parts[3]
            else:
                await event.answer("❌ Invalid order selection", alert=True)
                return
            
            if region in STORES and category in STORES[region]['categories'] and store_id in STORES[region]['categories'][category]['stores']:
                store = STORES[region]['categories'][category]['stores'][store_id]
                
                order_states[user_id] = {
                    'active': True,
                    'current_field': 'first_name',
                    'store_info': store,
                    'region': region,
                    'category': category,
                    'store_id': store_id,
                    'order_data': {}
                }
                
                await safe_edit(
                    event,
                    f"🛒 <b>New Order - {store['name']}</b>\n\n"
                    f"<i>Provide information step by step.</i>\n"
                    f"<i>Type /cancel to abort anytime.</i>\n\n"
                    f"👤 <b>First Name</b>\n"
                    f"<i>Enter your first name:</i>",
                    buttons=None
                )
        
        # Confirm order
        elif data == "confirm_order":
            if user_id in order_states:
                state = order_states[user_id]
                order_data = state['order_data']
                store_info = state['store_info']
                
                order_id = create_order(user_id, store_info, order_data)
                
                try:
                    order_total = float(order_data['order_total'])
                    # Use new fee format if available, otherwise fall back to old format
                    if 'fee' in store_info:
                        fee = calculate_fee(order_total, fee_string=store_info['fee'])
                        fee_display = store_info['fee']
                    else:
                        fee = calculate_fee(order_total, store_info.get('fee_percentage', 18), store_info.get('fee_fixed', 0))
                        fee_display = f"{store_info.get('fee_percentage', 18)}%"
                    # User only pays the fee
                    amount_to_pay = fee
                except:
                    fee = 0
                    amount_to_pay = 0
                    fee_display = "18%"
                
                user_data = get_user_data(user_id)
                user_name = user_data['name']
                
                # Get last 4 digits of order ID
                order_short = order_id.split('-')[-1][-4:]
                
                order_notification = (
                    f"🔔 <b>NEW ORDER RECEIVED</b>\n\n"
                    f"🆔 <code>{order_id}</code>\n"
                    f"👤 {user_name} (ID: {user_id})\n"
                    f"🏪 {store_info['name']}\n\n"
                    f"<b>💰 Financial</b>\n"
                    f"• Order Total: ${order_data['order_total']}\n"
                    f"• Fee ({fee_display}): ${fee}\n"
                    f"• <b>Customer Pays: ${amount_to_pay}</b>\n\n"
                    f"👤 {order_data['first_name']} {order_data['last_name']}\n"
                    f"📱 {order_data['phone_number']}\n\n"
                    f"📦 Order #: {order_data['order_number']}\n"
                    f"📍 Track: {order_data['track_number']}\n\n"
                    f"🔐 Login: {order_data['login_details']}\n"
                    f"📧 Mailbox: {order_data['mailbox_login']}\n\n"
                    f"🏠 Delivery:\n{order_data['delivery_address']}\n\n"
                    f"📮 Billing:\n{order_data['billing_address']}\n\n"
                    f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                admin_buttons = [
                    [Button.inline("✅ Accept", f"accept_{order_id}".encode()),
                     Button.inline("❌ Reject", f"reject_{order_id}".encode())],
                    [Button.inline("📝 Add Remark", f"remark_{order_id}".encode())]
                ]
                
                try:
                    await bot.send_message(ORDERS_CHANNEL_ID, order_notification, buttons=admin_buttons, parse_mode='html')
                except Exception as e:
                    log_error(f"Failed to send order to channel", e)
                
                success_msg = (
                    f"✅ <b>Order Submitted!</b>\n\n"
                    f"🆔 <code>{order_id}</code>\n"
                    f"🏪 {store_info['name']}\n"
                    f"💰 Your Fee: <code>${amount_to_pay}</code>\n\n"
                    f"📨 <b>Order is being reviewed</b>\n\n"
                    f"⏱ Estimated: <i>{store_info.get('timeframe', store_info.get('processing', 'TBD'))}</i>\n"
                    f"💬 Updates via DM\n\n"
                    f"📋 Check status in Profile\n\n"
                    f"✨ <b>Thank you for choosing Return's Portal!</b>"
                )
                
                buttons = [[Button.inline("👤 My Profile", b"profile"), Button.inline("🏠 Home", b"main_menu")]]
                
                await safe_edit(event, success_msg, buttons=buttons)
                
                del order_states[user_id]
        
        # Cancel order
        elif data == "cancel_order":
            if user_id in order_states:
                del order_states[user_id]
            
            await safe_edit(
                event,
                "❌ <b>Order Cancelled</b>\n\n<i>No charges were made.</i>",
                buttons=[[Button.inline("🛍️ Browse Stores", b"store_list"), Button.inline("🏠 Home", b"main_menu")]]
            )
        
        # Profile
        elif data == "profile":
            user_data = get_user_data(user_id)
            orders = load_json(orders_file)
            service_orders = load_json(service_orders_file)
            
            user_orders = [oid for oid in user_data.get('orders', []) if oid in orders]
            user_service_orders = [oid for oid in user_data.get('service_orders', []) if oid in service_orders]
            total_orders = len(user_orders)
            
            pending = sum(1 for oid in user_orders if orders[oid]['status'] == 'pending')
            completed = sum(1 for oid in user_orders if orders[oid]['status'] == 'completed')
            rejected = sum(1 for oid in user_orders if orders[oid]['status'] == 'rejected')
            
            wallet_balance = get_wallet_balance(user_id)
            
            message = (
                f"👤 <b>Your Profile</b>\n\n"
                f"<b>Personal Information</b>\n"
                f"• Name: {user_data['name']}\n"
                f"• User ID: <code>{user_id}</code>\n"
                f"• Member Since: {user_data['join_date']}\n\n"
                f"<b>💰 Wallet</b>\n"
                f"• Balance: <b>${wallet_balance:.2f} USD</b>\n\n"
                f"<b>📊 Order Statistics</b>\n"
                f"• Store Orders: <b>{total_orders}</b>\n"
                f"• Service Orders: <b>{len(user_service_orders)}</b>\n"
                f"• ⏳ Pending: {pending}\n"
                f"• ✅ Completed: {completed}\n"
                f"• ❌ Rejected: {rejected}\n\n"
            )
            
            if user_orders or user_service_orders:
                message += "<i>Use the buttons below to manage your account</i>"
            else:
                message += "<i>No orders yet. Start shopping!</i>"
            
            buttons = [
                [Button.inline("💰 Wallet", b"wallet"), Button.inline("📦 My Orders", b"my_orders")],
                [Button.inline("📊 Payment History", b"payment_history")],
                [Button.inline("🏠 Back to Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Wallet
        elif data == "wallet":
            balance = get_wallet_balance(user_id)
            
            message = (
                f"💰 <b>Your Wallet</b>\n\n"
                f"💵 <b>Current Balance:</b> ${balance:.2f} USD\n\n"
                f"<b>Quick Actions:</b>\n"
                f"• 💳 Deposit funds via cryptocurrency\n"
                f"• 📊 View your payment history\n"
                f"• 🛒 Use balance for purchases\n\n"
                f"<i>Fast, secure, and convenient!</i>"
            )
            
            buttons = [
                [Button.inline("💳 Deposit Funds", b"wallet_deposit")],
                [Button.inline("📊 Payment History", b"payment_history")],
                [Button.inline("🔙 Back to Profile", b"profile")],
                [Button.inline("🏠 Main Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Wallet deposit
        elif data == "wallet_deposit":
            deposit_states[user_id] = True
            
            message = (
                f"💳 <b>Deposit to Wallet</b>\n\n"
                f"<i>Enter the amount you want to deposit in USD:</i>\n\n"
                f"💡 Minimum: $1 USD\n\n"
                f"<b>Example:</b> 50"
            )
            
            buttons = [
                [Button.inline("❌ Cancel", b"wallet_cancel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Wallet cancel
        elif data == "wallet_cancel":
            if user_id in deposit_states:
                del deposit_states[user_id]
            
            message = (
                f"❌ <b>Deposit Cancelled</b>\n\n"
                f"<i>You can deposit funds anytime from your wallet.</i>"
            )
            
            buttons = [
                [Button.inline("💰 My Wallet", b"wallet")],
                [Button.inline("🏠 Main Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Payment history
        elif data == "payment_history":
            user_data = get_user_data(user_id)
            payment_history = user_data.get('payment_history', [])
            
            if not payment_history:
                message = (
                    f"📊 <b>Payment History</b>\n\n"
                    f"<i>No payment history found.</i>\n\n"
                    f"💡 Make your first deposit to get started!"
                )
                
                buttons = [
                    [Button.inline("💳 Deposit Now", b"wallet_deposit")],
                    [Button.inline("🔙 Back", b"wallet")],
                    [Button.inline("🏠 Main Menu", b"main_menu")]
                ]
            else:
                message = f"📊 <b>Payment History</b>\n\n"
                
                # Show last 10 transactions
                recent = payment_history[-10:][::-1]
                
                for transaction in recent:
                    amount = transaction['amount']
                    trans_type = transaction['type']
                    desc = transaction['description']
                    timestamp = transaction['timestamp']
                    
                    emoji = "💰" if amount > 0 else "💸"
                    sign = "+" if amount > 0 else ""
                    
                    message += (
                        f"{emoji} <b>{sign}${abs(amount):.2f}</b>\n"
                        f"<i>{desc}</i>\n"
                        f"🕐 {timestamp}\n\n"
                    )
                
                if len(payment_history) > 10:
                    message += f"<i>Showing 10 of {len(payment_history)} transactions</i>"
                
                buttons = [
                    [Button.inline("🔙 Back to Wallet", b"wallet")],
                    [Button.inline("🏠 Main Menu", b"main_menu")]
                ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # My Orders
        elif data == "my_orders":
            user_data = get_user_data(user_id)
            orders = load_json(orders_file)
            service_orders = load_json(service_orders_file)
            
            user_orders = [oid for oid in user_data.get('orders', []) if oid in orders]
            user_service_orders = [oid for oid in user_data.get('service_orders', []) if oid in service_orders]
            
            message = f"📦 <b>My Orders</b>\n\n<i>Select order type to view:</i>\n\n"
            
            message += f"🛍️ <b>Store Orders:</b> {len(user_orders)}\n"
            message += f"⚙️ <b>Service Orders:</b> {len(user_service_orders)}\n"
            
            buttons = []
            
            if user_orders:
                buttons.append([Button.inline("🛍️ Store Orders", b"view_store_orders")])
            
            if user_service_orders:
                buttons.append([Button.inline("⚙️ Service Orders", b"view_service_orders")])
            
            if not user_orders and not user_service_orders:
                message += "\n<i>No orders yet. Start shopping!</i>"
                buttons.append([Button.inline("🛍️ Browse Stores", b"store_list")])
            
            buttons.append([Button.inline("🔙 Back to Profile", b"profile")])
            buttons.append([Button.inline("🏠 Main Menu", b"main_menu")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # View store orders
        elif data == "view_store_orders":
            user_data = get_user_data(user_id)
            orders = load_json(orders_file)
            
            user_orders = [oid for oid in user_data.get('orders', []) if oid in orders]
            
            if not user_orders:
                await event.answer("❌ No store orders found", alert=True)
                return
            
            message = f"🛍️ <b>Store Orders</b>\n\n<i>Click an order to view details:</i>\n\n"
            
            buttons = []
            recent = user_orders[-10:][::-1]
            
            for oid in recent:
                order = orders[oid]
                status_emoji = {"pending": "⏳", "completed": "✅", "rejected": "❌"}
                emoji = status_emoji.get(order['status'], '📦')
                short_id = oid.split('-')[-1][-4:]
                store_name = order['store_info']['name'][:20]
                
                buttons.append([Button.inline(f"{emoji} ...{short_id} - {store_name}", f"view_order_{oid}".encode())])
            
            buttons.append([Button.inline("🔙 Back", b"my_orders")])
            buttons.append([Button.inline("🏠 Main Menu", b"main_menu")])
            
            await safe_edit(event, message, buttons=buttons)

        # View service orders
        elif data == "view_service_orders":
            user_data = get_user_data(user_id)
            service_orders = load_json(service_orders_file)
            
            user_service_orders = [oid for oid in user_data.get('service_orders', []) if oid in service_orders]
            
            if not user_service_orders:
                await event.answer("❌ No service orders found", alert=True)
                return
            
            message = f"⚙️ <b>Service Orders</b>\n\n<i>Click an order to view details:</i>\n\n"
            
            buttons = []
            recent = user_service_orders[-10:][::-1]
            
            for oid in recent:
                order = service_orders[oid]
                status_emoji = {"pending": "⏳", "completed": "✅", "rejected": "❌"}
                emoji = status_emoji.get(order['status'], '📦')
                short_id = oid.split('-')[-1][-4:]
                service_name = order['service_name'][:20]
                
                buttons.append([Button.inline(f"{emoji} ...{short_id} - {service_name}", f"view_service_order_{oid}".encode())])
            
            buttons.append([Button.inline("🔙 Back", b"my_orders")])
            buttons.append([Button.inline("🏠 Main Menu", b"main_menu")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # View individual order
        elif data.startswith("view_order_"):
            order_id = data.replace("view_order_", "")
            order = get_order(order_id)
            
            if not order or order['user_id'] != user_id:
                await event.answer("❌ Order not found", alert=True)
                return
            
            status_map = {"pending": "⏳ Pending", "completed": "✅ Completed", "rejected": "❌ Rejected"}
            status_text = status_map.get(order['status'], order['status'])
            
            payment_status_map = {"unpaid": "❌ Unpaid", "paid": "✅ Paid", "pending": "⏳ Pending"}
            payment_text = payment_status_map.get(order.get('payment_status', 'unpaid'), order.get('payment_status', 'unpaid'))
            
            try:
                total = float(order['order_data']['order_total'])
                fee = calculate_fee(total, order['store_info']['fee_percentage'], order['store_info']['fee_fixed'])
                total_with_fee = total + fee
            except:
                fee = 0
                total_with_fee = 0
            
            message = (
                f"📦 <b>Order Details</b>\n\n"
                f"🆔 <code>{order_id}</code>\n"
                f"📊 Status: {status_text}\n"
                f"💳 Payment: {payment_text}\n\n"
                f"🏪 {order['store_info']['name']}\n"
                f"💰 Amount: ${order['order_data']['order_total']}\n"
                f"💵 Fee: ${fee}\n"
                f"💸 Total: <b>${total_with_fee}</b>\n\n"
                f"📅 Ordered: {order['timestamp']}\n"
                f"📦 Order #: {order['order_data']['order_number']}\n"
                f"📍 Track: {order['order_data']['track_number']}\n\n"
            )
            
            if order.get('remarks'):
                message += "<b>📝 Updates & Remarks</b>\n\n"
                for remark in order['remarks'][-5:]:
                    message += f"• <b>{remark['by']}</b> ({remark['timestamp']}):\n<i>{remark['text']}</i>\n\n"
            else:
                message += "<i>No updates yet</i>"
            
            buttons = [
                [Button.inline("🔙 Back to Orders", b"view_store_orders")],
                [Button.inline("🏠 Main Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # View individual service order
        elif data.startswith("view_service_order_"):
            order_id = data.replace("view_service_order_", "")
            order = get_service_order(order_id)
            
            if not order or order['user_id'] != user_id:
                await event.answer("❌ Order not found", alert=True)
                return
            
            status_map = {"pending": "⏳ Pending", "completed": "✅ Completed", "rejected": "❌ Rejected"}
            status_text = status_map.get(order['status'], order['status'])
            
            payment_status_map = {"unpaid": "❌ Unpaid", "paid": "✅ Paid"}
            payment_text = payment_status_map.get(order.get('payment_status', 'unpaid'), order.get('payment_status', 'unpaid'))
            
            message = (
                f"⚙️ <b>Service Order Details</b>\n\n"
                f"🆔 <code>{order_id}</code>\n"
                f"📊 Status: {status_text}\n"
                f"💳 Payment: {payment_text}\n\n"
                f"📦 Service: {order['service_name']}\n"
                f"💰 Price: ${order['price']}\n"
                f"📅 Ordered: {order['timestamp']}\n\n"
            )
            
            # Show delivery content if completed
            if order['status'] == 'completed' and order.get('delivery_content'):
                message += "<b>✅ Order Delivered</b>\n\n"
                if order['delivery_content'].get('content'):
                    message += f"<i>{order['delivery_content']['content']}</i>\n\n"
                message += f"<i>Delivered: {order['delivery_content']['timestamp']}</i>"
            else:
                message += "<i>⏳ Waiting for delivery...</i>"
            
            buttons = [
                [Button.inline("🔙 Back to Orders", b"view_service_orders")],
                [Button.inline("🏠 Main Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin: Accept order
        elif data.startswith("accept_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("accept_", "")
            
            if update_order(order_id, {'status': 'accepted'}):
                add_order_remark(order_id, "✅ Order accepted by admin - Pending payment")
                
                order = get_order(order_id)
                customer_id = order['user_id']
                
                await bot.send_message(
                    customer_id,
                    f"✅ <b>Order Accepted!</b>\n\n"
                    f"🆔 <code>{order_id}</code>\n"
                    f"🏪 {order['store_info']['name']}\n\n"
                    f"⏳ <i>Waiting for admin to request payment...</i>",
                    parse_mode='html'
                )
                
                try:
                    msg = await event.get_message()
                    original_text = msg.message
                    
                    # Add Ask Payment button
                    new_buttons = [
                        [Button.inline("💰 Ask Payment", f"ask_payment_{order_id}".encode())],
                        [Button.inline("📝 Add Remark", f"remark_{order_id}".encode())],
                        [Button.inline("❌ Reject", f"reject_{order_id}".encode())]
                    ]
                    
                    await event.edit(
                        original_text + "\n\n✅ <b>ACCEPTED - Awaiting Payment Request</b>",
                        buttons=new_buttons,
                        parse_mode='html'
                    )
                except Exception as e:
                    log_error("Failed to edit message after accept", e)
                
                await event.answer("✅ Order accepted!", alert=True)
        
        # Admin: Ask payment
        elif data.startswith("ask_payment_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("ask_payment_", "")
            order = get_order(order_id)
            
            if not order:
                await event.answer("❌ Order not found", alert=True)
                return
            
            try:
                total = float(order['order_data']['order_total'])
                fee = calculate_fee(total, order['store_info']['fee_percentage'], order['store_info']['fee_fixed'])
                total_with_fee = total + fee
            except:
                total_with_fee = 0
            
            customer_id = order['user_id']
            customer_balance = get_wallet_balance(customer_id)
            
            # Create payment message for customer
            payment_message = (
                f"💰 <b>Payment Request</b>\n\n"
                f"🆔 Order: <code>{order_id}</code>\n"
                f"🏪 Store: {order['store_info']['name']}\n\n"
                f"<b>💵 Payment Details:</b>\n"
                f"• Order Total: ${order['order_data']['order_total']}\n"
                f"• Processing Fee: ${fee}\n"
                f"• <b>Total Amount: ${total_with_fee}</b>\n\n"
                f"💰 Your Wallet: <b>${customer_balance:.2f}</b>\n\n"
                f"<i>Choose payment method:</i>"
            )
            
            payment_buttons = [
                [Button.inline("💳 Pay with Wallet", f"pay_wallet_{order_id}".encode())],
                [Button.inline("🪙 Pay with Crypto", f"pay_crypto_{order_id}".encode())]
            ]
            
            await bot.send_message(customer_id, payment_message, buttons=payment_buttons, parse_mode='html')
            
            add_order_remark(order_id, f"💰 Payment request sent - Amount: ${total_with_fee}")
            
            await event.answer("✅ Payment request sent to customer!", alert=True)
        
        # Pay with wallet
        elif data.startswith("pay_wallet_"):
            order_id = data.replace("pay_wallet_", "")
            order = get_order(order_id)
            
            if not order or order['user_id'] != user_id:
                await event.answer("❌ Order not found", alert=True)
                return
            
            try:
                total = float(order['order_data']['order_total'])
                fee = calculate_fee(total, order['store_info']['fee_percentage'], order['store_info']['fee_fixed'])
                total_with_fee = total + fee
            except:
                await event.answer("❌ Error calculating amount", alert=True)
                return
            
            # Check wallet balance
            balance = get_wallet_balance(user_id)
            
            if balance < total_with_fee:
                await event.answer(f"❌ Insufficient balance. You need ${total_with_fee:.2f} but have ${balance:.2f}", alert=True)
                return
            
            # Deduct from wallet
            if deduct_from_wallet(user_id, total_with_fee, f"Order Payment - {order_id}"):
                update_order(order_id, {'payment_status': 'paid', 'status': 'processing'})
                add_order_remark(order_id, f"✅ Payment received via wallet - ${total_with_fee}")
                
                await event.answer("✅ Payment successful!", alert=True)
                
                # Log order payment to logs channel
                user_entity = await bot.get_entity(user_id)
                user_name = f"{user_entity.first_name or ''} {user_entity.last_name or ''}".strip()
                user_username = user_entity.username or "No username"
                await send_log_to_channel(
                    "💰 ORDER PAYMENT",
                    f"Order Payment via Wallet\nOrder ID: {order_id}\nAmount: ${total_with_fee}\nStore: {order['store_info']['name']}\nUsername: @{user_username}",
                    user_id=user_id,
                    username=user_name
                )
                
                # Notify user
                await bot.send_message(
                    user_id,
                    f"✅ <b>Payment Successful!</b>\n\n"
                    f"🆔 Order: <code>{order_id}</code>\n"
                    f"💰 Amount: ${total_with_fee}\n"
                    f"💳 Method: Wallet\n\n"
                    f"⏳ <i>Your order is now being processed!</i>",
                    parse_mode='html'
                )
                
                # Notify admin
                try:
                    user_data = get_user_data(user_id)
                    await notify_admins(
                        f"💰 <b>Payment Received!</b>\n\n"
                        f"🆔 Order: <code>{order_id}</code>\n"
                        f"👤 User: {user_data['name']} (<code>{user_id}</code>)\n"
                        f"💵 Amount: ${total_with_fee}\n"
                        f"💳 Method: Wallet\n\n"
                        f"✅ <i>Ready to complete order</i>",
                        buttons=[[Button.inline("✅ Complete Order", f"complete_order_{order_id}".encode())]]
                    )
                except Exception as e:
                    log_error("Failed to notify admin about payment", e)
                
                await safe_edit(
                    event,
                    "✅ <b>Payment Completed!</b>\n\n<i>Your order is being processed...</i>",
                    buttons=[[Button.inline("📦 View Order", f"view_order_{order_id}".encode()), Button.inline("🏠 Home", b"main_menu")]]
                )
            else:
                await event.answer("❌ Payment failed. Please try again.", alert=True)
        
        # Pay with crypto
        elif data.startswith("pay_crypto_"):
            order_id = data.replace("pay_crypto_", "")
            order = get_order(order_id)
            
            if not order or order['user_id'] != user_id:
                await event.answer("❌ Order not found", alert=True)
                return
            
            try:
                total = float(order['order_data']['order_total'])
                fee = calculate_fee(total, order['store_info']['fee_percentage'], order['store_info']['fee_fixed'])
                total_with_fee = total + fee
            except:
                await event.answer("❌ Error calculating amount", alert=True)
                return
            
            # Create payment
            payment_link, payment_id = await create_payment(
                user_id,
                total_with_fee,
                f"Order Payment - {order_id}",
                f"ORDER-{order_id}"
            )
            
            if payment_link:
                # Link payment to order
                payments = load_json(payments_file)
                if payment_id in payments:
                    payments[payment_id]['order_id'] = order_id
                    save_json(payments_file, payments)
                
                message = format_payment_message(total_with_fee, payment_link, payment_id, 120, "Crypto Payment", "Order will be processed automatically", order_id)
                
                buttons = [
                    [Button.url("💳 Pay Now", payment_link)],
                    [Button.inline("🔄 Check Status", f"check_order_payment_{payment_id}".encode())],
                    [Button.inline("🏠 Main Menu", b"main_menu")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
                # Start countdown in background (using event as msg since safe_edit edits the event)
                asyncio.create_task(show_payment_countdown(event, user_id, total_with_fee, payment_link, payment_id, 'order', "Crypto Payment", "Order will be processed automatically", order_id, f"check_order_payment_{payment_id}"))
            else:
                await event.answer("❌ Payment error. Please try again.", alert=True)
        
        # Check order payment
        elif data.startswith("check_order_payment_"):
            payment_id = data.replace("check_order_payment_", "")
            
            status = await check_payment_status(payment_id)
            
            if status == 'completed':
                payments = load_json(payments_file)
                payment_data = payments.get(payment_id)
                
                if payment_data and payment_data.get('order_id'):
                    # Check if payment was already processed
                    if payment_data.get('processed'):
                        await event.answer("✅ Payment already processed!", alert=True)
                        return
                    
                    order_id = payment_data['order_id']
                    amount = payment_data['amount']
                    
                    # Mark payment as processed
                    payment_data['processed'] = True
                    payment_data['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    payments[payment_id] = payment_data
                    save_json(payments_file, payments)
                    
                    # Update order
                    update_order(order_id, {'payment_status': 'paid', 'status': 'processing'})
                    add_order_remark(order_id, f"✅ Payment received via crypto - ${amount}")
                    
                    order = get_order(order_id)
                    
                    # Log crypto payment to logs channel
                    user_entity = await bot.get_entity(user_id)
                    user_name = f"{user_entity.first_name or ''} {user_entity.last_name or ''}".strip()
                    user_username = user_entity.username or "No username"
                    await send_log_to_channel(
                        "💰 CRYPTO PAYMENT",
                        f"Order Payment via Cryptocurrency\nOrder ID: {order_id}\nAmount: ${amount}\nStore: {order['store_info']['name']}\nPayment ID: {payment_id}\nUsername: @{user_username}",
                        user_id=user_id,
                        username=user_name
                    )
                    
                    # Notify user
                    await bot.send_message(
                        user_id,
                        f"✅ <b>Payment Successful!</b>\n\n"
                        f"🆔 Order: <code>{order_id}</code>\n"
                        f"💰 Amount: ${amount}\n"
                        f"💳 Method: Cryptocurrency\n\n"
                        f"⏳ <i>Your order is now being processed!</i>",
                        parse_mode='html'
                    )
                    
                    # Notify admin
                    try:
                        user_data = get_user_data(user_id)
                        await bot.send_message(
                            PAYMENT_NOTIFICATION_CHANNEL,
                            f"💰 <b>Order Payment Received!</b>\n\n"
                            f"🆔 Order: <code>{order_id}</code>\n"
                            f"👤 User: {user_data['name']} (<code>{user_id}</code>)\n"
                            f"🏪 Store: {order['store_info']['name']}\n"
                            f"💵 Amount: ${amount}\n"
                            f"💳 Method: Cryptocurrency\n\n"
                            f"✅ <i>Ready to complete order</i>",
                            buttons=[[Button.inline("✅ Complete Order", f"complete_order_{order_id}".encode())]],
                            parse_mode='html'
                        )
                    except Exception as e:
                        log_error("Failed to notify admin about order payment", e)
                    
                    await safe_edit(
                        event,
                        "✅ <b>Payment Completed!</b>\n\n<i>Your order is being processed...</i>",
                        buttons=[[Button.inline("📦 View Order", f"view_order_{order_id}".encode()), Button.inline("🏠 Home", b"main_menu")]]
                    )
                    
                    await event.answer("✅ Payment successful!", alert=True)
                else:
                    await event.answer("❌ Order not found", alert=True)
            elif status == 'failed':
                await event.answer("❌ Payment expired or failed", alert=True)
            else:
                await event.answer("⏳ Payment is still pending", alert=False)
        
        # Admin: Complete order
        elif data.startswith("complete_order_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("complete_order_", "")
            
            admin_complete_order_states[user_id] = {'order_id': order_id}
            
            await bot.send_message(
                user_id,
                f"📦 <b>Complete Order</b>\n\n"
                f"🆔 <code>{order_id}</code>\n\n"
                f"<i>Send the order completion message/file to deliver to customer:</i>\n\n"
                f"💡 You can send text, images, or files\n"
                f"📝 Type /cancel to abort",
                parse_mode='html'
            )
            
            await event.answer("📝 Send completion content in DM", alert=True)
        
        # Admin: Final complete order
        elif data.startswith("admin_final_complete_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("admin_final_complete_", "")
            
            if user_id not in admin_complete_order_states:
                await event.answer("❌ Session expired", alert=True)
                return
            
            state = admin_complete_order_states[user_id]
            delivery_content = state.get('delivery_content')
            
            # Update order status
            update_order(order_id, {'status': 'completed'})
            add_order_remark(order_id, "✅ Order completed and delivered")
            
            order = get_order(order_id)
            customer_id = order['user_id']
            
            # Send to customer
            try:
                if delivery_content['type'] == 'media':
                    await bot.send_file(
                        customer_id,
                        delivery_content['file_path'],
                        caption=f"✅ <b>Order Completed!</b>\n\n🆔 <code>{order_id}</code>\n\n<i>Thank you for your order!</i>",
                        parse_mode='html'
                    )
                else:
                    await bot.send_message(
                        customer_id,
                        f"✅ <b>Order Completed!</b>\n\n"
                        f"🆔 <code>{order_id}</code>\n\n"
                        f"<b>Delivery:</b>\n{delivery_content['content']}\n\n"
                        f"<i>Thank you for your order!</i>",
                        parse_mode='html'
                    )
                
                await event.answer("✅ Order completed and delivered!", alert=True)
                await event.edit("✅ <b>Order Completed!</b>\n\n<i>Customer has been notified</i>", parse_mode='html')
                
                del admin_complete_order_states[user_id]
            except Exception as e:
                log_error("Failed to deliver completed order", e)
                await event.answer("❌ Failed to deliver order", alert=True)
        
        # Admin: Cancel complete
        elif data == "admin_cancel_complete":
            if user_id in admin_complete_order_states:
                del admin_complete_order_states[user_id]
            await event.answer("❌ Cancelled", alert=False)
        
        # Admin: Reject order
        elif data.startswith("reject_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("reject_", "")
            
            if update_order(order_id, {'status': 'rejected'}):
                add_order_remark(order_id, "❌ Order rejected by admin")
                
                order = get_order(order_id)
                customer_id = order['user_id']
                
                await bot.send_message(
                    customer_id,
                    f"❌ <b>Order Rejected</b>\n\n"
                    f"🆔 <code>{order_id}</code>\n\n"
                    f"<i>Your order has been rejected. Contact support for more info.</i>",
                    parse_mode='html'
                )
                
                try:
                    msg = await event.get_message()
                    original_text = msg.message
                    await event.edit(
                        original_text + "\n\n❌ <b>REJECTED BY ADMIN</b>",
                        buttons=None,
                        parse_mode='html'
                    )
                except Exception as e:
                    log_error("Failed to edit message after reject", e)
                
                await event.answer("❌ Order rejected!", alert=True)
        
        # Admin: Complete service order
        elif data.startswith("complete_service_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("complete_service_", "")
            
            admin_complete_order_states[user_id] = {'order_id': order_id, 'is_service': True}
            
            await bot.send_message(
                user_id,
                f"📦 <b>Complete Service Order</b>\n\n"
                f"🆔 <code>{order_id}</code>\n\n"
                f"<i>Send the service delivery content:</i>\n\n"
                f"💡 You can send text, images, or files\n"
                f"📝 Type /cancel to abort",
                parse_mode='html'
            )
            
            await event.answer("📝 Send completion content in DM", alert=True)
        
        # Admin: Start chat for service order
        elif data.startswith("start_chat_service_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("start_chat_service_", "")
            service_order = get_service_order(order_id)
            
            if service_order:
                customer_id = service_order['user_id']
                
                try:
                    user_entity = await bot.get_entity(customer_id)
                    user_name = user_entity.first_name or "User"
                    
                    ticket_id = create_ticket(customer_id, f"Support for order {order_id}", user_name)
                    update_ticket(ticket_id, {'status': 'active'})
                    
                    await bot.send_message(
                        customer_id,
                        f"✅ <b>Support Chat Started</b>\n\n"
                        f"🆔 Order: <code>{order_id}</code>\n"
                        f"🎫 Ticket: <code>{ticket_id}</code>\n\n"
                        f"💬 Admin has started a chat with you\n\n"
                        f"<i>Type /endchat to close</i>",
                        parse_mode='html'
                    )
                    
                    await notify_admins(
                        f"✅ <b>Chat Started</b>\n\n"
                        f"👤 User: {user_name}\n"
                        f"🆔 Order: <code>{order_id}</code>\n"
                        f"🎫 Ticket: <code>{ticket_id}</code>\n\n"
                        f"<i>Type /endchat to close</i>"
                    )
                    
                    await event.answer("✅ Chat started!", alert=True)
                except Exception as e:
                    log_error("Failed to start chat", e)
                    await event.answer("❌ Failed to start chat", alert=True)
        
        # Method Store - Main Menu
        elif data == "method_store":
            user_data = get_user_data(user_id)
            username = user_data['name']
            balance = user_data.get('wallet_balance', 0)
            
            message = (
                f"🌟 <b>Welcome {username} to Return's Method Store Bot</b>\n\n"
                f"💰 <b>Your Balance:</b> ${balance:.2f}\n\n"
                f"<i>Choose an option below to get started:</i>"
            )
            
            buttons = [
                [Button.inline("🛒 Purchase Methods", b"purchase_methods"), Button.inline("📦 My Methods", b"my_methods")],
                [Button.inline("💳 Deposit Funds", b"wallet_deposit"), Button.inline("📞 Support", b"support")],
                [Button.inline("🏠 Back to Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Purchase Methods - Region Selection
        elif data == "purchase_methods":
            all_methods = get_all_methods()
            
            if not all_methods:
                await safe_edit(
                    event,
                    "📭 <b>No Methods Available</b>\n\n<i>No methods are currently available for purchase. Check back later!</i>",
                    buttons=[[Button.inline("🔙 Method Store", b"method_store"), Button.inline("🏠 Home", b"main_menu")]]
                )
                return
            
            # Count methods per region
            regions_count = {
                'UK': len(get_methods_by_region('UK')),
                'EU': len(get_methods_by_region('EU')),
                'USA': len(get_methods_by_region('USA')),
                'CANADA': len(get_methods_by_region('CANADA')),
                'Worldwide': len(get_methods_by_region('Worldwide'))
            }
            
            message = (
                "🌍 <b>Select Region</b>\n\n"
                "<i>Choose your region to browse available methods:</i>\n\n"
                f"🇬🇧 <b>UK</b> - {regions_count['UK']} methods\n"
                f"🇪🇺 <b>EU</b> - {regions_count['EU']} methods\n"
                f"🇺🇸 <b>USA</b> - {regions_count['USA']} methods\n"
                f"🇨🇦 <b>CANADA</b> - {regions_count['CANADA']} methods\n"
                f"🌐 <b>Worldwide</b> - {regions_count['Worldwide']} methods\n\n"
                "⚡ <i>Premium methods for all regions</i>"
            )
            
            buttons = [
                [Button.inline("🇬🇧 UK", b"method_region_UK"), Button.inline("🇪🇺 EU", b"method_region_EU")],
                [Button.inline("🇺🇸 USA", b"method_region_USA"), Button.inline("🇨🇦 CANADA", b"method_region_CANADA")],
                [Button.inline("🌐 Worldwide", b"method_region_Worldwide")],
                [Button.inline("🔙 Method Store", b"method_store"), Button.inline("🏠 Home", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # View Methods by Region
        elif data.startswith("method_region_"):
            region = data.replace("method_region_", "")
            methods = get_methods_by_region(region)
            
            if not methods:
                await safe_edit(
                    event,
                    f"📭 <b>No Methods in {region}</b>\n\n<i>No methods are currently available for this region. Check other regions!</i>",
                    buttons=[[Button.inline("🔙 Regions", b"purchase_methods"), Button.inline("🏠 Home", b"main_menu")]]
                )
                return
            
            region_flags = {
                'UK': '🇬🇧',
                'EU': '🇪🇺',
                'USA': '🇺🇸',
                'CANADA': '🇨🇦',
                'Worldwide': '🌐'
            }
            
            message = f"{region_flags.get(region, '🌐')} <b>{region} Methods</b>\n\n<i>Select a method below:</i>\n\n✨ <b>Total Methods: {len(methods)}</b>"
            
            buttons = []
            for method_id, method in methods.items():
                buttons.append([Button.inline(f"{method['name']} - ${method['price']:.2f}", f"view_method_{method_id}".encode())])
            
            buttons.append([Button.inline("🔙 Regions", b"purchase_methods"), Button.inline("🏠 Home", b"main_menu")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # View Method Details
        elif data.startswith("view_method_"):
            method_id = data.replace("view_method_", "")
            method = get_method(method_id)
            
            if not method:
                await event.answer("❌ Method not found!", alert=True)
                return
            
            user_data = get_user_data(user_id)
            has_purchased = has_purchased_method(user_id, method_id)
            
            tags_str = ", ".join(method.get('tags', [])) if method.get('tags') else "No tags"
            region_flags = {'UK': '🇬🇧', 'EU': '🇪🇺', 'USA': '🇺🇸', 'CANADA': '🇨🇦', 'Worldwide': '🌐'}
            region = method.get('region', 'Worldwide')
            
            message = (
                f"📖 <b>{method['name']}</b>\n\n"
                f"🌍 <b>Region:</b> {region_flags.get(region, '🌐')} {region}\n"
                f"💰 <b>Price:</b> ${method['price']}\n"
                f"🏷️ <b>Tags:</b> {tags_str}\n\n"
            )
            
            if method.get('description'):
                message += f"📝 <b>Description:</b>\n{method['description']}\n\n"
            
            if has_purchased:
                message += "✅ <b>You already own this method!</b>\n\n"
                
                buttons = [
                    [Button.inline("📥 Download Method", f"download_method_{method_id}".encode())],
                    [Button.inline("🔙 Browse Methods", b"purchase_methods"), Button.inline("🏠 Home", b"main_menu")]
                ]
            else:
                message += f"💼 <b>Your Balance:</b> ${user_data.get('wallet_balance', 0):.2f}\n\n"
                message += "<i>Click 'Buy Now' to purchase this method</i>"
                
                buttons = [
                    [Button.inline("💳 Buy Now", f"buy_method_{method_id}".encode())],
                    [Button.inline("🔙 Browse Methods", b"purchase_methods"), Button.inline("🏠 Home", b"main_menu")]
                ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Buy Method
        elif data.startswith("buy_method_"):
            method_id = data.replace("buy_method_", "")
            method = get_method(method_id)
            
            if not method:
                await event.answer("❌ Method not found!", alert=True)
                return
            
            if has_purchased_method(user_id, method_id):
                await event.answer("✅ You already own this method!", alert=True)
                return
            
            user_data = get_user_data(user_id)
            balance = user_data.get('wallet_balance', 0)
            price = float(method['price'])
            
            if balance < price:
                await event.answer(f"❌ Insufficient balance! You need ${price - balance:.2f} more", alert=True)
                return
            
            # Deduct from balance
            new_balance = balance - price
            update_wallet(user_id, new_balance)
            
            # Add purchase
            add_method_purchase(user_id, method_id)
            
            # Send success message
            message = (
                f"✅ <b>Purchase Successful!</b>\n\n"
                f"📖 <b>Method:</b> {method['name']}\n"
                f"💰 <b>Price:</b> ${price:.2f}\n"
                f"💼 <b>New Balance:</b> ${new_balance:.2f}\n\n"
                f"<i>You can now download your method!</i>"
            )
            
            buttons = [
                [Button.inline("📥 Download Method", f"download_method_{method_id}".encode())],
                [Button.inline("📦 My Methods", b"my_methods"), Button.inline("🏠 Home", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
            
            # Notify admins
            await notify_admins(
                f"💰 <b>Method Purchased!</b>\n\n"
                f"👤 User: {user_data['name']} (ID: {user_id})\n"
                f"📖 Method: {method['name']}\n"
                f"💵 Amount: ${price:.2f}"
            )
        
        # Download Method
        elif data.startswith("download_method_"):
            method_id = data.replace("download_method_", "")
            method = get_method(method_id)
            
            if not method:
                await event.answer("❌ Method not found!", alert=True)
                return
            
            if not has_purchased_method(user_id, method_id):
                await event.answer("❌ You don't own this method!", alert=True)
                return
            
            # Send method details
            message = (
                f"📥 <b>{method['name']}</b>\n\n"
                f"<b>Method Details:</b>\n"
                f"{method.get('description', 'No description available')}\n\n"
            )
            
            if method.get('tags'):
                message += f"🏷️ <b>Tags:</b> {', '.join(method['tags'])}\n\n"
            
            message += "<i>Files are being sent to you...</i>"
            
            await event.respond(message, parse_mode='html')
            
            # Send files if available
            if method.get('pdf_file'):
                try:
                    await bot.send_file(user_id, method['pdf_file'], caption=f"📄 <b>{method['name']} - PDF Document</b>", parse_mode='html')
                except:
                    pass
            
            if method.get('image_file'):
                try:
                    await bot.send_file(user_id, method['image_file'], caption=f"🖼️ <b>{method['name']} - Preview Image</b>", parse_mode='html')
                except:
                    pass
            
            await event.answer("✅ Method sent to your DM!", alert=False)
        
        # My Methods
        elif data == "my_methods":
            user_methods = get_user_methods(user_id)
            
            if not user_methods:
                message = (
                    "📭 <b>No Methods Purchased</b>\n\n"
                    "<i>You haven't purchased any methods yet. Browse available methods to get started!</i>"
                )
                
                buttons = [
                    [Button.inline("🛒 Browse Methods", b"purchase_methods")],
                    [Button.inline("🔙 Method Store", b"method_store"), Button.inline("🏠 Home", b"main_menu")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
                return
            
            message = "📦 <b>My Methods</b>\n\n<i>Select a method to download:</i>\n\n"
            
            buttons = []
            for purchase in user_methods:
                method = get_method(purchase['method_id'])
                if method:
                    message += f"✅ <b>{method['name']}</b>\n💰 ${method['price']} - Purchased: {purchase['purchased_at']}\n\n"
                    buttons.append([Button.inline(f"📥 {method['name']}", f"download_method_{method['id']}".encode())])
            
            buttons.append([Button.inline("🔙 Method Store", b"method_store"), Button.inline("🏠 Home", b"main_menu")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin: Reject service order
        elif data.startswith("reject_service_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("reject_service_", "")
            
            if update_service_order(order_id, {'status': 'rejected'}):
                service_order = get_service_order(order_id)
                customer_id = service_order['user_id']
                
                await bot.send_message(
                    customer_id,
                    f"❌ <b>Service Order Rejected</b>\n\n"
                    f"🆔 <code>{order_id}</code>\n\n"
                    f"<i>Your order has been rejected. Contact support for more info.</i>",
                    parse_mode='html'
                )
                
                await event.answer("❌ Service order rejected!", alert=True)
        
        # Admin: Add remark
        elif data.startswith("remark_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("remark_", "")
            
            admin_remark_state[user_id] = {'order_id': order_id}
            
            await bot.send_message(
                user_id,
                f"📝 <b>Add Remark to Order</b>\n\n"
                f"🆔 <code>{order_id}</code>\n\n"
                f"<i>Send your remark message in DM:</i>\n\n"
                f"(Type /cancel to abort)",
                parse_mode='html'
            )
            
            await event.answer("📝 Send remark in bot DM", alert=True)
        
        # Admin Panel
        elif data == "admin_panel":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            orders = load_json(orders_file)
            service_orders = load_json(service_orders_file)
            tickets = load_json(tickets_file)
            raffles = load_json(raffles_file)
            users = get_all_users()
            
            all_orders = list(orders.keys())
            pending = [o for o in all_orders if orders[o]['status'] == 'pending']
            processing = [o for o in all_orders if orders[o]['status'] in ['accepted', 'processing']]
            completed = [o for o in all_orders if orders[o]['status'] == 'completed']
            
            service_pending = [o for o in service_orders.keys() if service_orders[o]['status'] == 'pending']
            service_completed = [o for o in service_orders.keys() if service_orders[o]['status'] == 'completed']
            
            active_tickets = [t for t, data in tickets.items() if data['status'] == 'active']
            pending_tickets = [t for t, data in tickets.items() if data['status'] == 'pending']
            
            active_raffles = [r for r, data in raffles.items() if data['status'] == 'active']
            
            message = (
                f"🔧 <b>Admin Panel</b>\n\n"
                f"<b>📊 Statistics</b>\n\n"
                f"<b>Users:</b>\n"
                f"• Total Users: {len(users)}\n\n"
                f"<b>Store Orders:</b>\n"
                f"• Total: {len(all_orders)}\n"
                f"• ⏳ Pending: {len(pending)}\n"
                f"• ⚙️ Processing: {len(processing)}\n"
                f"• ✅ Completed: {len(completed)}\n\n"
                f"<b>Service Orders:</b>\n"
                f"• ⏳ Pending: {len(service_pending)}\n"
                f"• ✅ Completed: {len(service_completed)}\n\n"
                f"<b>Support Tickets:</b>\n"
                f"• 💬 Active: {len(active_tickets)}\n"
                f"• ⏳ Pending: {len(pending_tickets)}\n\n"
                f"<b>Raffles:</b>\n"
                f"• 🎁 Active: {len(active_raffles)}\n\n"
                f"<i>Select an option:</i>"
            )
            
            buttons = [
                [Button.inline("📦 Store Orders", b"admin_orders"),
                 Button.inline("⚙️ Service Orders", b"admin_service_orders")],
                [Button.inline("🎫 Tickets", b"admin_tickets"),
                 Button.inline("👥 User Stats", b"admin_user_stats")],
                [Button.inline("🎁 Create Raffle", b"create_raffle"),
                 Button.inline("📊 Error Logs", b"admin_logs")],
                [Button.inline("🌟 Method Store", b"admin_method_store"),
                 Button.inline("📢 Broadcast", b"admin_broadcast")],
                [Button.inline("📝 Form Edits", b"admin_form")],
                [Button.inline("➕ Add Services To Sell", b"admin_add_service")],
                [Button.inline("💰 Reseller Pricing", b"admin_reseller_pricing")],
                [Button.inline("🏠 Back to Menu", b"main_menu")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin: Resources Management
        elif data == "admin_resources":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            current_link = get_resources_link()
            
            message = (
                f"📚 <b>Resources Management</b>\n\n"
                f"<b>Current Link:</b>\n"
                f"{current_link}\n\n"
                f"<i>Click below to update the link:</i>"
            )
            
            buttons = [
                [Button.inline("✏️ Update Link", b"update_resources_link")],
                [Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin: Update Resources Link
        elif data == "update_resources_link":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            admin_resources_state[user_id] = {'awaiting_link': True}
            
            await event.answer("✏️ Send new link in chat", alert=True)
            
            await bot.send_message(
                user_id,
                "📚 <b>Update Resources Link</b>\n\n"
                "Please send the new resources link:",
                parse_mode='html'
            )
        
        # Links Menu (User Button)
        elif data == "links_menu":
            # Generate all 4 invite links
            links = await generate_all_invite_links()
            
            if links:
                buttons = [
                    [Button.inline("Browse Return's Hub ⚡️", b"browse_hub")]
                ]
                
                # Show invite with countdown in background
                asyncio.create_task(show_all_links_with_countdown(event, links, buttons, is_edit=True))
            else:
                await event.answer("❌ Failed to generate invite links. Please try again later.", alert=True)
        
        # Join Resources (User Button)
        elif data == "join_resources":
            # Generate invite links
            links = await generate_invite_links()
            
            if links:
                buttons = [
                    [Button.inline("Browse Return's Hub ⚡️", b"browse_hub")]
                ]
                
                # Show invite with countdown in background
                asyncio.create_task(show_invite_with_countdown(event, links, buttons, is_edit=True))
            else:
                await event.answer("❌ Failed to generate invite links. Please try again later.", alert=True)
        
        # Admin Method Store Main
        elif data == "admin_method_store":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            methods = get_all_methods()
            method_count = len(methods)
            
            # Count methods per region
            regions_count = {
                'UK': len(get_methods_by_region('UK')),
                'EU': len(get_methods_by_region('EU')),
                'USA': len(get_methods_by_region('USA')),
                'CANADA': len(get_methods_by_region('CANADA')),
                'Worldwide': len(get_methods_by_region('Worldwide'))
            }
            
            message = (
                f"🌟 <b>Method Store Management</b>\n\n"
                f"📊 <b>Statistics:</b>\n"
                f"📖 Total Methods: {method_count}\n\n"
                f"<b>By Region:</b>\n"
                f"🇬🇧 UK: {regions_count['UK']} | 🇪🇺 EU: {regions_count['EU']}\n"
                f"🇺🇸 USA: {regions_count['USA']} | 🇨🇦 CANADA: {regions_count['CANADA']}\n"
                f"🌐 Worldwide: {regions_count['Worldwide']}\n\n"
                f"<i>Choose an action below:</i>"
            )
            
            buttons = [
                [Button.inline("➕ Add Method", b"admin_add_method"), Button.inline("✏️ Edit Method", b"admin_edit_method_select")],
                [Button.inline("🗑️ Delete Method", b"admin_delete_method_select"), Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin Add Method - Region Selection
        elif data == "admin_add_method":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            message = (
                "🌍 <b>Add Method - Select Region</b>\n\n"
                "<i>First, select which region this method is for:</i>\n\n"
                "🇬🇧 <b>UK</b> - United Kingdom only\n"
                "🇪🇺 <b>EU</b> - European Union\n"
                "🇺🇸 <b>USA</b> - United States only\n"
                "🇨🇦 <b>CANADA</b> - Canada only\n"
                "🌐 <b>Worldwide</b> - All regions\n\n"
                "💡 <i>Choose carefully - this determines who can see the method</i>"
            )
            
            buttons = [
                [Button.inline("🇬🇧 UK", b"add_method_UK"), Button.inline("🇪🇺 EU", b"add_method_EU")],
                [Button.inline("🇺🇸 USA", b"add_method_USA"), Button.inline("🇨🇦 CANADA", b"add_method_CANADA")],
                [Button.inline("🌐 Worldwide", b"add_method_Worldwide")],
                [Button.inline("❌ Cancel", b"admin_method_store")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin Add Method - Start Input
        elif data.startswith("add_method_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            region = data.replace("add_method_", "")
            
            admin_method_state[user_id] = {
                'action': 'add',
                'step': 'info',
                'region': region
            }
            
            region_flags = {
                'UK': '🇬🇧',
                'EU': '🇪🇺',
                'USA': '🇺🇸',
                'CANADA': '🇨🇦',
                'Worldwide': '🌐'
            }
            
            message = (
                f"➕ <b>Add Method (Super Easy)</b>\n"
                f"{region_flags.get(region, '🌐')} <b>Region: {region}</b>\n\n"
                "<b>Step 1: Send Method Info</b>\n\n"
                "Just send me the method info in ANY simple format:\n\n"
                "<b>Simple Format:</b>\n"
                "<code>PayPal Method 25.99</code>\n\n"
                "<b>Detailed Format:</b>\n"
                "<code>Name: PayPal Method\n"
                "Price: 25.99\n"
                "Description: Premium PayPal method (optional)\n"
                "Tags: uk, usa, worldwide (optional)</code>\n\n"
                "<b>Step 2: Upload Files (Optional)</b>\n\n"
                "After creating the method:\n"
                "• Send a PDF file to attach documents\n"
                "• Send an image to add a method preview\n"
                "• No need for external links\n"
                "• Files stored securely on server\n"
                "• Users get files sent directly to them\n\n"
                "<b>Examples:</b>\n"
                "<code>Stripe Method $15</code>\n"
                "<code>Name: Bank Method, Price:30</code>\n"
                "<code>Venmo Guide = 20.50</code>\n\n"
                "Ready? Send the method info first! 🚀"
            )
            
            await safe_edit(event, message, buttons=[[Button.inline("❌ Cancel", b"admin_method_store")]], parse_mode='html')
        
        # Admin Edit Method - Select
        elif data == "admin_edit_method_select":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            methods = get_all_methods()
            
            if not methods:
                await event.answer("❌ No methods available to edit!", alert=True)
                return
            
            message = "✏️ <b>Edit Method</b>\n\n<i>Select a method to edit:</i>\n\n"
            
            buttons = []
            for method_id, method in methods.items():
                region = method.get('region', 'Worldwide')
                region_flags = {'UK': '🇬🇧', 'EU': '🇪🇺', 'USA': '🇺🇸', 'CANADA': '🇨🇦', 'Worldwide': '🌐'}
                message += f"{region_flags.get(region, '🌐')} {method['name']} - ${method['price']} ({region})\n"
                buttons.append([Button.inline(f"✏️ {method['name']}", f"admin_edit_method_{method_id}".encode())])
            
            buttons.append([Button.inline("🔙 Method Store", b"admin_method_store")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin Edit Method - Start
        elif data.startswith("admin_edit_method_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            method_id = data.replace("admin_edit_method_", "")
            method = get_method(method_id)
            
            if not method:
                await event.answer("❌ Method not found!", alert=True)
                return
            
            admin_method_state[user_id] = {
                'action': 'edit',
                'method_id': method_id,
                'step': 'menu'
            }
            
            region_flags = {'UK': '🇬🇧', 'EU': '🇪🇺', 'USA': '🇺🇸', 'CANADA': '🇨🇦', 'Worldwide': '🌐'}
            region = method.get('region', 'Worldwide')
            
            message = (
                f"✏️ <b>Edit Method: {method['name']}</b>\n\n"
                f"🌍 Region: {region_flags.get(region, '🌐')} {region}\n"
                f"💰 Current Price: ${method['price']}\n"
                f"📝 Description: {method.get('description', 'None')}\n"
                f"🏷️ Tags: {', '.join(method.get('tags', [])) if method.get('tags') else 'None'}\n"
                f"📄 PDF: {'✅ Attached' if method.get('pdf_file') else '❌ No file'}\n"
                f"🖼️ Image: {'✅ Attached' if method.get('image_file') else '❌ No file'}\n\n"
                "<i>What would you like to update?</i>"
            )
            
            buttons = [
                [Button.inline("💰 Update Price", f"edit_method_price_{method_id}".encode()), Button.inline("📝 Update Description", f"edit_method_desc_{method_id}".encode())],
                [Button.inline("🏷️ Update Tags", f"edit_method_tags_{method_id}".encode()), Button.inline("🌍 Change Region", f"edit_method_region_{method_id}".encode())],
                [Button.inline("📄 Update PDF", f"edit_method_pdf_{method_id}".encode()), Button.inline("🖼️ Update Image", f"edit_method_img_{method_id}".encode())],
                [Button.inline("🔙 Back", b"admin_edit_method_select")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin Delete Method - Select
        elif data == "admin_delete_method_select":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            methods = get_all_methods()
            
            if not methods:
                await event.answer("❌ No methods available to delete!", alert=True)
                return
            
            message = "🗑️ <b>Delete Method</b>\n\n<i>Select a method to delete:</i>\n\n"
            
            buttons = []
            for method_id, method in methods.items():
                region = method.get('region', 'Worldwide')
                region_flags = {'UK': '🇬🇧', 'EU': '🇪🇺', 'USA': '🇺🇸', 'CANADA': '🇨🇦', 'Worldwide': '🌐'}
                message += f"{region_flags.get(region, '🌐')} {method['name']} - ${method['price']} ({region})\n"
                buttons.append([Button.inline(f"🗑️ {method['name']}", f"admin_delete_method_{method_id}".encode())])
            
            buttons.append([Button.inline("🔙 Method Store", b"admin_method_store")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin Delete Method - Confirm
        elif data.startswith("admin_delete_method_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            method_id = data.replace("admin_delete_method_", "")
            method = get_method(method_id)
            
            if not method:
                await event.answer("❌ Method not found!", alert=True)
                return
            
            if delete_method(method_id):
                await event.answer(f"✅ {method['name']} deleted successfully!", alert=True)
                
                # Return to method store management
                methods = get_all_methods()
                method_count = len(methods)
                
                message = (
                    f"🌟 <b>Method Store Management</b>\n\n"
                    f"📊 <b>Statistics:</b>\n"
                    f"📖 Total Methods: {method_count}\n\n"
                    f"<i>✅ Method deleted successfully!</i>"
                )
                
                buttons = [
                    [Button.inline("➕ Add Method", b"admin_add_method"), Button.inline("✏️ Edit Method", b"admin_edit_method_select")],
                    [Button.inline("🗑️ Delete Method", b"admin_delete_method_select"), Button.inline("🔙 Admin Panel", b"admin_panel")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
            else:
                await event.answer("❌ Failed to delete method!", alert=True)
        
        # Admin Broadcast Main
        elif data == "admin_broadcast":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            broadcast_state[user_id] = {'waiting': True}
            
            message = (
                "📢 <b>Broadcast Message</b>\n\n"
                "<i>Send the message you want to broadcast to all users.</i>\n\n"
                "💡 You can send:\n"
                "• Text messages\n"
                "• Images with captions\n"
                "• Videos with captions\n"
                "• Documents\n\n"
                "Send /cancel to cancel."
            )
            
            await safe_edit(event, message, buttons=None)
        
        # Finish Method - With Broadcast
        elif data.startswith("finish_method_") and "_broadcast" in data:
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            method_id = data.replace("finish_method_", "").replace("_broadcast", "")
            method = get_method(method_id)
            
            if not method:
                await event.answer("❌ Method not found!", alert=True)
                return
            
            # Clean up state
            if user_id in admin_method_state:
                del admin_method_state[user_id]
            
            # Broadcast to all users
            users = get_all_users()
            success_count = 0
            
            broadcast_message = (
                "🎉 <b>NEW METHOD AVAILABLE!</b> 🎉\n\n"
                f"📖 <b>{method['name']}</b>\n"
                f"💰 <b>Price:</b> ${method['price']}\n\n"
            )
            
            if method.get('description'):
                broadcast_message += f"📝 {method['description']}\n\n"
            
            if method.get('tags'):
                broadcast_message += f"🏷️ <b>Tags:</b> {', '.join(method['tags'])}\n\n"
            
            broadcast_message += "<i>🛒 Visit Method Store to purchase now!</i>"
            
            for user in users:
                try:
                    await bot.send_message(int(user), broadcast_message, parse_mode='html')
                    success_count += 1
                    await asyncio.sleep(0.05)  # Rate limit
                except:
                    pass
            
            await event.answer(f"✅ Method published! Broadcasted to {success_count} users!", alert=True)
            
            # Return to method store management
            methods = get_all_methods()
            message = (
                f"🌟 <b>Method Store Management</b>\n\n"
                f"📊 <b>Statistics:</b>\n"
                f"📖 Total Methods: {len(methods)}\n\n"
                f"✅ <b>{method['name']}</b> published and broadcasted to {success_count} users!"
            )
            
            buttons = [
                [Button.inline("➕ Add Another Method", b"admin_add_method"), Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Finish Method - No Broadcast
        elif data.startswith("finish_method_") and "_no" in data:
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            method_id = data.replace("finish_method_", "").replace("_no", "")
            method = get_method(method_id)
            
            if not method:
                await event.answer("❌ Method not found!", alert=True)
                return
            
            # Clean up state
            if user_id in admin_method_state:
                del admin_method_state[user_id]
            
            await event.answer(f"✅ {method['name']} published successfully!", alert=True)
            
            # Return to method store management
            methods = get_all_methods()
            message = (
                f"🌟 <b>Method Store Management</b>\n\n"
                f"📊 <b>Statistics:</b>\n"
                f"📖 Total Methods: {len(methods)}\n\n"
                f"✅ <b>{method['name']}</b> published successfully!"
            )
            
            buttons = [
                [Button.inline("➕ Add Another Method", b"admin_add_method"), Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Cancel Method Creation
        elif data.startswith("cancel_method_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            method_id = data.replace("cancel_method_", "")
            method = get_method(method_id)
            
            if method and delete_method(method_id):
                await event.answer(f"❌ {method['name']} cancelled and deleted!", alert=True)
            
            # Clean up state
            if user_id in admin_method_state:
                del admin_method_state[user_id]
            
            # Return to admin method store
            methods = get_all_methods()
            message = (
                f"🌟 <b>Method Store Management</b>\n\n"
                f"📊 <b>Statistics:</b>\n"
                f"📖 Total Methods: {len(methods)}\n\n"
                f"<i>Choose an action below:</i>"
            )
            
            buttons = [
                [Button.inline("➕ Add Method", b"admin_add_method"), Button.inline("✏️ Edit Method", b"admin_edit_method_select")],
                [Button.inline("🗑️ Delete Method", b"admin_delete_method_select"), Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin: Form Management
        elif data == "admin_form":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            current_link = get_form_link()
            
            message = (
                f"📝 <b>Form Management</b>\n\n"
                f"<b>Current Form Link:</b>\n"
                f"{current_link}\n\n"
                f"<i>Click below to update the form link:</i>"
            )
            
            buttons = [
                [Button.inline("✏️ Update Link", b"update_form_link")],
                [Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin: Update Form Link
        elif data == "update_form_link":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            admin_form_state[user_id] = {'awaiting_link': True}
            
            await event.answer("✏️ Send new form link in chat", alert=True)
            
            await bot.send_message(
                user_id,
                "📝 <b>Update Form Link</b>\n\n"
                "Please send the new form link:",
                parse_mode='html'
            )
        
        # Admin: Add Service To Sell
        elif data == "admin_add_service":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            # Start service creation flow
            admin_service_state[user_id] = {'step': 'name'}
            
            await bot.send_message(
                user_id,
                "➕ <b>Add New Service</b>\n\n"
                "📝 <b>Step 1/3:</b> Service Name\n\n"
                "Please send the service name:\n"
                "<i>(e.g., 'Premium Support', 'Custom Bot Setup')</i>\n\n"
                "Type /cancel to abort",
                parse_mode='html'
            )
            
            await event.answer("✏️ Send service details in chat", alert=True)
        
        # Admin: Reseller Pricing Management
        elif data == "admin_reseller_pricing":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            reseller_pricing = get_reseller_pricing()
            
            message = (
                f"💰 <b>Reseller Pricing Management</b>\n\n"
                f"<i>Set custom pricing for resellers by User ID</i>\n\n"
                f"<b>Available Services:</b>\n"
                f"• ftid - FTID Service\n"
                f"• rts_dmg - RTS + DMG Service\n"
                f"• ups_lit - UPS LIT Service\n\n"
            )
            
            if reseller_pricing:
                message += "<b>Current Resellers:</b>\n"
                for user, prices in reseller_pricing.items():
                    message += f"\n👤 User ID: <code>{user}</code>\n"
                    for service, price in prices.items():
                        message += f"  • {service}: ${price}\n"
            else:
                message += "<i>No custom pricing set yet</i>"
            
            buttons = [
                [Button.inline("➕ Add/Update Pricing", b"add_reseller_pricing")],
                [Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin: Add/Update Reseller Pricing
        elif data == "add_reseller_pricing":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            admin_reseller_state[user_id] = {'step': 'user_id'}
            
            await bot.send_message(
                user_id,
                "💰 <b>Set Reseller Pricing</b>\n\n"
                "📝 <b>Step 1/3:</b> User ID\n\n"
                "Please send the user ID of the reseller:\n"
                "<i>(Numerical ID only)</i>\n\n"
                "Type /cancel to abort",
                parse_mode='html'
            )
            
            await event.answer("✏️ Send user ID in chat", alert=True)
        
        # Admin: Service Orders
        elif data == "admin_service_orders":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            service_orders = load_json(service_orders_file)
            
            pending = [oid for oid, o in service_orders.items() if o['status'] == 'pending']
            completed = [oid for oid, o in service_orders.items() if o['status'] == 'completed']
            rejected = [oid for oid, o in service_orders.items() if o['status'] == 'rejected']
            
            message = (
                f"⚙️ <b>Service Orders Management</b>\n\n"
                f"<b>Statistics:</b>\n"
                f"• ⏳ Pending: {len(pending)}\n"
                f"• ✅ Completed: {len(completed)}\n"
                f"• ❌ Rejected: {len(rejected)}\n\n"
                f"<i>Select category:</i>"
            )
            
            buttons = [
                [Button.inline("⏳ Pending", b"admin_service_pending_0")],
                [Button.inline("✅ Completed", b"admin_service_completed_0")],
                [Button.inline("❌ Rejected", b"admin_service_rejected_0")],
                [Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin: Service orders by status
        elif data.startswith("admin_service_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            parts = data.split("_")
            status = parts[2]
            page = int(parts[3])
            
            service_orders = load_json(service_orders_file)
            filtered = [oid for oid, o in service_orders.items() if o['status'] == status]
            filtered.sort(key=lambda x: service_orders[x]['timestamp'], reverse=True)
            
            per_page = 10
            start = page * per_page
            end = start + per_page
            page_orders = filtered[start:end]
            
            total_pages = max(1, (len(filtered) + per_page - 1) // per_page)
            
            status_name = {"pending": "⏳ Pending", "completed": "✅ Completed", "rejected": "❌ Rejected"}
            
            message = (
                f"⚙️ <b>{status_name.get(status, status)} Service Orders</b>\n"
                f"<i>Page {page + 1} of {total_pages}</i>\n\n"
            )
            
            if page_orders:
                buttons = []
                for oid in page_orders:
                    order = service_orders[oid]
                    short_id = oid.split('-')[-1][-4:]
                    try:
                        user_entity = await bot.get_entity(order['user_id'])
                        user_name = user_entity.first_name or "User"
                        button_text = f"...{short_id} - {user_name[:10]}"
                    except:
                        button_text = f"...{short_id}"
                    
                    buttons.append([Button.inline(button_text, f"admin_view_service_{oid}".encode())])
            else:
                message += "<i>No orders found</i>"
                buttons = []
            
            nav = []
            if page > 0:
                nav.append(Button.inline("⬅️ Prev", f"admin_service_{status}_{page-1}".encode()))
            if end < len(filtered):
                nav.append(Button.inline("Next ➡️", f"admin_service_{status}_{page+1}".encode()))
            
            if nav:
                buttons.append(nav)
            
            buttons.append([Button.inline("🔙 Service Orders", b"admin_service_orders")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin: View individual service order
        elif data.startswith("admin_view_service_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("admin_view_service_", "")
            order = get_service_order(order_id)
            
            if not order:
                await event.answer("❌ Order not found", alert=True)
                return
            
            status_map = {"pending": "⏳ Pending", "completed": "✅ Completed", "rejected": "❌ Rejected"}
            status_text = status_map.get(order['status'], order['status'])
            
            payment_status_map = {"unpaid": "❌ Unpaid", "paid": "✅ Paid"}
            payment_text = payment_status_map.get(order.get('payment_status', 'unpaid'), order.get('payment_status', 'unpaid'))
            
            message = (
                f"⚙️ <b>Service Order Details (Admin View)</b>\n\n"
                f"🆔 <code>{order_id}</code>\n"
                f"📊 Status: {status_text}\n"
                f"💳 Payment: {payment_text}\n\n"
                f"👤 Customer ID: <code>{order['user_id']}</code>\n"
                f"📦 Service: {order['service_name']}\n"
                f"💰 Price: ${order['price']}\n"
                f"📅 Ordered: {order['timestamp']}\n\n"
            )
            
            # Show order data if available
            if order.get('order_data'):
                message += "<b>📋 Order Details:</b>\n"
                for key, value in order['order_data'].items():
                    if key not in ['file_path', 'payment_id']:
                        message += f"• {key.replace('_', ' ').title()}: {value}\n"
                message += "\n"
            
            buttons = []
            
            if order['status'] == 'pending' and order.get('payment_status') == 'paid':
                buttons.append([
                    Button.inline("✅ Complete", f"complete_service_{order_id}".encode()),
                    Button.inline("❌ Reject", f"reject_service_{order_id}".encode())
                ])
                buttons.append([Button.inline("💬 Start Chat", f"start_chat_service_{order_id}".encode())])
            
            buttons.append([Button.inline("🔙 Back", b"admin_service_orders")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # Vouches
        elif data == "vouches":
            try:
                expire_time = datetime.now() + timedelta(seconds=60)
                
                invite = await bot(ExportChatInviteRequest(
                    peer=VOUCHES_CHANNEL_ID,
                    expire_date=int(expire_time.timestamp()),
                    usage_limit=1,
                    request_needed=False
                ))
                
                invite_link = invite.link
                
                # Schedule auto-revoke after 60 seconds
                asyncio.create_task(revoke_invite_links(
                    {'vouches': {'link': invite_link, 'channel_id': VOUCHES_CHANNEL_ID}}, 
                    60
                ))
                
                message = (
                    f"⭐ <b>Join Our Vouches Channel!</b>\n\n"
                    f"<i>📢 Channel:</i> <b>Return's Vouches</b>\n"
                    f"<i>🔗 Thousands of verified reviews</i>\n\n"
                    f"⏱ <i>Link expires in</i> <b>60 seconds</b>\n"
                    f"⚡ <i>Click below to join!</i>\n\n"
                    f"🔒 <i>One-time use for security</i>"
                )
                
                buttons = [
                    [Button.url("🌟 Join Channel", invite_link)],
                    [Button.inline("🔙 Back", b"main_menu")]
                ]
                
                await safe_edit(event, message, buttons=buttons)
                await event.answer("✅ Link generated!", alert=False)
                
            except Exception as e:
                log_error("Vouches link error", e)
                await event.answer(f"❌ Error generating link", alert=True)
        
        # Main Menu
        elif data == "main_menu":
            try:
                await event.delete()
            except:
                pass
            
            await send_main_menu(user_id)
        
        # Broadcast
        elif data == "confirm_broadcast":
            if not is_admin(user_id):
                await event.answer("❌ Not authorized!", alert=True)
                return
            
            if user_id not in broadcast_state:
                await event.answer("❌ No message!", alert=True)
                return
            
            await event.answer("📢 Broadcasting...", alert=False)
            await event.edit("📢 <b>Broadcasting...</b>", parse_mode='html')
            
            broadcast_msg = broadcast_state[user_id]['message']
            users = get_all_users()
            total = len(users)
            
            if total == 0:
                await event.edit("❌ No users!")
                del broadcast_state[user_id]
                return
            
            success = blocked = 0
            
            for idx, uid in enumerate(users, 1):
                try:
                    await bot.send_message(uid, broadcast_msg)
                    success += 1
                except:
                    blocked += 1
                
                if idx % 10 == 0:
                    try:
                        await event.edit(
                            f"📢 <b>Broadcasting...</b>\n\n"
                            f"{idx}/{total} ({int(idx/total*100)}%)\n"
                            f"✅ {success} | 🚫 {blocked}",
                            parse_mode='html'
                        )
                    except:
                        pass
                
                await asyncio.sleep(0.05)
            
            await event.edit(
                f"✅ <b>Complete!</b>\n\n"
                f"Total: {total}\n"
                f"✅ Success: {success}\n"
                f"🚫 Blocked: {blocked}\n"
                f"📈 Rate: {int(success/total*100)}%",
                parse_mode='html'
            )
            
            del broadcast_state[user_id]
        
        elif data == "cancel_broadcast":
            if user_id in broadcast_state:
                del broadcast_state[user_id]
            await event.edit("❌ <b>Cancelled</b>", parse_mode='html')
        
        # Raffle creation
        elif data == "create_raffle":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            raffle_creation_state[user_id] = {'current_field': 'prize'}
            
            await safe_edit(
                event,
                f"🎁 <b>Create New Raffle</b>\n\n"
                f"🏆 <b>Prize Description</b>\n\n"
                f"<i>What's the prize for this raffle?</i>\n\n"
                f"Example: iPhone 15 Pro Max\n\n"
                f"💡 Send /cancel to abort",
                buttons=None
            )
        
        elif data == "create_raffle_confirm":
            if not is_admin(user_id) or user_id not in raffle_creation_state:
                return
            
            state = raffle_creation_state[user_id]
            
            raffle_id = create_raffle(
                state['prize'],
                state['winners_count'],
                state['duration_minutes']
            )
            
            raffle = get_raffle(raffle_id)
            end_time = datetime.fromisoformat(raffle['end_time'])
            
            channel_message = (
                f"🎁 <b>NEW RAFFLE!</b>\n\n"
                f"🏆 Prize: <b>{state['prize']}</b>\n"
                f"👥 Winners: <b>{state['winners_count']}</b>\n"
                f"⏰ Ends: <b>{end_time.strftime('%Y-%m-%d %H:%M:%S')}</b>\n\n"
                f"<i>Join the raffle through the bot!</i>\n\n"
                f"🎲 Good luck to all participants!"
            )
            
            try:
                await bot.send_message(VOUCHES_CHANNEL_ID, channel_message, parse_mode='html')
                
                await event.edit(
                    f"✅ <b>Raffle Created!</b>\n\n"
                    f"🎁 Raffle ID: <code>{raffle_id}</code>\n"
                    f"🏆 Prize: {state['prize']}\n"
                    f"👥 Winners: {state['winners_count']}\n"
                    f"⏱ Duration: {state['duration_minutes']} minutes\n\n"
                    f"<i>Raffle has been posted to the channel!</i>",
                    buttons=[[Button.inline("🔙 Admin Panel", b"admin_panel")]],
                    parse_mode='html'
                )
            except Exception as e:
                log_error("Failed to post raffle", e)
                await event.edit("❌ Failed to post raffle", parse_mode='html')
            
            del raffle_creation_state[user_id]
        
        elif data == "cancel_raffle":
            if user_id in raffle_creation_state:
                del raffle_creation_state[user_id]
            
            await safe_edit(
                event,
                "❌ <b>Raffle Creation Cancelled</b>",
                buttons=[[Button.inline("🔙 Admin Panel", b"admin_panel")]],
            )
        
        # Admin logs
        elif data == "admin_logs":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            if os.path.exists('logs/errors.log'):
                try:
                    with open('logs/errors.log', 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    recent = lines[-100:][::-1]
                    log_text = "".join(recent) if recent else "No errors"
                    
                    with open('logs/recent_errors.txt', 'w', encoding='utf-8') as f:
                        f.write(log_text)
                    
                    await bot.send_file(user_id, 'logs/recent_errors.txt', caption="📊 <b>Recent Error Logs</b>", parse_mode='html')
                    
                    await event.answer("✅ Logs sent", alert=False)
                except Exception as e:
                    log_error("Failed to send logs", e)
                    await event.answer(f"❌ Error", alert=True)
            else:
                await event.answer("✅ No errors logged", alert=True)
        
        # Admin user stats (already handled earlier)
        elif data == "admin_user_stats":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            users = get_all_users()
            user_data_all = load_json(user_data_file)
            orders = load_json(orders_file)
            
            total_users = len(users)
            users_with_orders = sum(1 for uid in users if str(uid) in user_data_all and user_data_all[str(uid)].get('orders'))
            total_referrals = sum(len(data.get('referrals', [])) for data in user_data_all.values())
            
            message = (
                f"👥 <b>User Statistics</b>\n\n"
                f"<b>Overview:</b>\n"
                f"• Total Users: {total_users}\n"
                f"• Users with Orders: {users_with_orders}\n"
                f"• Total Referrals: {total_referrals}\n\n"
                f"<i>Download detailed report for complete user data</i>"
            )
            
            buttons = [
                [Button.inline("📥 Download User Data", b"download_user_data")],
                [Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        elif data == "download_user_data":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            users = get_all_users()
            user_data_all = load_json(user_data_file)
            orders = load_json(orders_file)
            
            report_file = f"logs/user_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("USER DATABASE REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Total Users: {len(users)}\n")
                f.write(f"Total Orders: {len(orders)}\n\n")
                f.write("=" * 80 + "\n\n")
                
                for user_id_loop in users:
                    user_data = user_data_all.get(str(user_id_loop), {})
                    
                    f.write(f"User ID: {user_id_loop}\n")
                    f.write(f"Name: {user_data.get('name', 'N/A')}\n")
                    f.write(f"Join Date: {user_data.get('join_date', 'N/A')}\n")
                    f.write(f"Referral Code: {user_data.get('referral_code', 'N/A')}\n")
                    f.write(f"Referred By: {user_data.get('referred_by', 'None')}\n")
                    f.write(f"Total Referrals: {len(user_data.get('referrals', []))}\n")
                    f.write(f"Total Orders: {len(user_data.get('orders', []))}\n")
                    f.write(f"Wallet Balance: ${user_data.get('wallet_balance', 0):.2f}\n")
                    
                    user_orders = user_data.get('orders', [])
                    if user_orders:
                        f.write("Orders:\n")
                        for order_id in user_orders:
                            if order_id in orders:
                                order = orders[order_id]
                                f.write(f"  - {order_id} | {order['status']} | {order['timestamp']}\n")
                    
                    f.write("\n" + "-" * 80 + "\n\n")
            
            await bot.send_file(
                user_id,
                report_file,
                caption=f"📊 <b>Detailed User Report</b>\n\n<i>Total Users: {len(users)}</i>",
                parse_mode='html'
            )
            
            await event.answer("✅ Report sent!", alert=False)
        
        # Admin orders (already handled in part 6a)
        elif data == "admin_orders":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            message = (
                f"📦 <b>Order Management</b>\n\n"
                f"<i>Select order category:</i>"
            )
            
            buttons = [
                [Button.inline("⏳ Pending Orders", b"admin_orders_pending_0")],
                [Button.inline("⚙️ Processing Orders", b"admin_orders_processing_0")],
                [Button.inline("✅ Completed Orders", b"admin_orders_completed_0")],
                [Button.inline("❌ Rejected Orders", b"admin_orders_rejected_0")],
                [Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        elif data.startswith("admin_orders_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            parts = data.split("_")
            status = parts[2]
            page = int(parts[3])
            
            orders = load_json(orders_file)
            
            # Handle processing status (accepted or processing)
            if status == "processing":
                filtered = [oid for oid, o in orders.items() if o['status'] in ['accepted', 'processing']]
            else:
                filtered = [oid for oid, o in orders.items() if o['status'] == status]
            
            filtered.sort(key=lambda x: orders[x]['timestamp'], reverse=True)
            
            per_page = 10
            start = page * per_page
            end = start + per_page
            page_orders = filtered[start:end]
            
            total_pages = max(1, (len(filtered) + per_page - 1) // per_page)
            
            status_name = {
                "pending": "⏳ Pending", 
                "processing": "⚙️ Processing",
                "completed": "✅ Completed", 
                "rejected": "❌ Rejected"
            }
            
            message = (
                f"📦 <b>{status_name.get(status, status)} Orders</b>\n"
                f"<i>Page {page + 1} of {total_pages}</i>\n\n"
            )
            
            if page_orders:
                buttons = []
                for oid in page_orders:
                    order = orders[oid]
                    short_id = oid.split('-')[-1][-4:]
                    try:
                        user_entity = await bot.get_entity(order['user_id'])
                        user_name = user_entity.first_name or "User"
                        button_text = f"...{short_id} - {user_name[:10]}"
                    except:
                        button_text = f"...{short_id}"
                    
                    buttons.append([Button.inline(button_text, f"admin_view_order_{oid}".encode())])
            else:
                message += "<i>No orders found</i>"
                buttons = []
            
            nav = []
            if page > 0:
                nav.append(Button.inline("⬅️ Prev", f"admin_orders_{status}_{page-1}".encode()))
            if end < len(filtered):
                nav.append(Button.inline("Next ➡️", f"admin_orders_{status}_{page+1}".encode()))
            
            if nav:
                buttons.append(nav)
            
            buttons.append([Button.inline("🔙 Orders Menu", b"admin_orders")])
            
            await safe_edit(event, message, buttons=buttons)
        
        elif data.startswith("admin_view_order_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            order_id = data.replace("admin_view_order_", "")
            order = get_order(order_id)
            
            if not order:
                await event.answer("❌ Order not found", alert=True)
                return
            
            try:
                total = float(order['order_data']['order_total'])
                fee = calculate_fee(total, order['store_info']['fee_percentage'], order['store_info']['fee_fixed'])
                total_with_fee = total + fee
            except:
                fee = 0
                total_with_fee = 0
            
            message = (
                f"📦 <b>Order Details (Admin View)</b>\n\n"
                f"🆔 <code>{order_id}</code>\n"
                f"📊 Status: {order['status']}\n"
                f"💳 Payment: {order.get('payment_status', 'unpaid')}\n\n"
                f"👤 Customer ID: <code>{order['user_id']}</code>\n"
                f"🏪 {order['store_info']['name']}\n"
                f"💰 Amount: ${order['order_data']['order_total']}\n"
                f"💵 Fee: ${fee}\n"
                f"💸 Total: <b>${total_with_fee}</b>\n\n"
                f"📅 Ordered: {order['timestamp']}\n"
            )
            
            buttons = []
            
            if order['status'] == 'pending':
                buttons.append([
                    Button.inline("✅ Accept", f"accept_{order_id}".encode()),
                    Button.inline("❌ Reject", f"reject_{order_id}".encode())
                ])
            elif order['status'] in ['accepted', 'processing'] and order.get('payment_status') == 'paid':
                buttons.append([Button.inline("✅ Complete Order", f"complete_order_{order_id}".encode())])
            
            buttons.append([Button.inline("📝 Add Remark", f"remark_{order_id}".encode())])
            buttons.append([Button.inline("🔙 Back", b"admin_orders")])
            
            await safe_edit(event, message, buttons=buttons)
        
        # Admin tickets (similar structure)
        elif data == "admin_tickets":
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            message = (
                f"🎫 <b>Support Tickets</b>\n\n"
                f"<i>Select ticket category:</i>"
            )
            
            buttons = [
                [Button.inline("💬 Active Tickets", b"admin_tickets_active_0")],
                [Button.inline("⏳ Pending Tickets", b"admin_tickets_pending_0")],
                [Button.inline("✅ Closed Tickets", b"admin_tickets_closed_0")],
                [Button.inline("🔙 Admin Panel", b"admin_panel")]
            ]
            
            await safe_edit(event, message, buttons=buttons)
        
        elif data.startswith("admin_tickets_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            parts = data.split("_")
            status = parts[2]
            page = int(parts[3])
            
            tickets = load_json(tickets_file)
            filtered = [tid for tid, t in tickets.items() if t['status'] == status]
            filtered.sort(key=lambda x: tickets[x]['timestamp'], reverse=True)
            
            per_page = 10
            start = page * per_page
            end = start + per_page
            page_tickets = filtered[start:end]
            
            total_pages = max(1, (len(filtered) + per_page - 1) // per_page)
            
            status_name = {"active": "💬 Active", "pending": "⏳ Pending", "closed": "✅ Closed"}
            
            message = (
                f"🎫 <b>{status_name.get(status, status)} Tickets</b>\n"
                f"<i>Page {page + 1} of {total_pages}</i>\n\n"
            )
            
            if page_tickets:
                buttons = []
                for tid in page_tickets:
                    ticket = tickets[tid]
                    short_id = tid.split('-')[-1][-4:]
                    buttons.append([Button.inline(f"🎫 ...{short_id} - {ticket['user_name'][:10]}", f"admin_view_ticket_{tid}".encode())])
            else:
                message += "<i>No tickets found</i>"
                buttons = []
            
            nav = []
            if page > 0:
                nav.append(Button.inline("⬅️ Prev", f"admin_tickets_{status}_{page-1}".encode()))
            if end < len(filtered):
                nav.append(Button.inline("Next ➡️", f"admin_tickets_{status}_{page+1}".encode()))
            
            if nav:
                buttons.append(nav)
            
            buttons.append([Button.inline("🔙 Tickets Menu", b"admin_tickets")])
            
            await safe_edit(event, message, buttons=buttons)
        
        elif data.startswith("admin_view_ticket_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            ticket_id = data.replace("admin_view_ticket_", "")
            ticket = get_ticket(ticket_id)
            
            if not ticket:
                await event.answer("❌ Ticket not found", alert=True)
                return
            
            user_link = f"<a href='tg://user?id={ticket['user_id']}'>{ticket['user_name']}</a>"
            
            message = (
                f"🎫 <b>Ticket Details</b>\n\n"
                f"🆔 <code>{ticket_id}</code>\n"
                f"📊 Status: {ticket['status']}\n\n"
                f"👤 User: {user_link}\n"
                f"🆔 User ID: <code>{ticket['user_id']}</code>\n\n"
                f"<b>Question:</b>\n<i>{ticket['question']}</i>\n\n"
                f"📅 Created: {ticket['timestamp']}\n\n"
            )
            
            if ticket['messages']:
                message += f"<b>Messages: {len(ticket['messages'])}</b>"
            else:
                message += "<i>No messages yet</i>"
            
            buttons = [[Button.inline("📄 Get Transcript", f"ticket_transcript_{ticket_id}".encode())]]
            buttons.append([Button.inline("🔙 Back", b"admin_tickets")])
            
            await safe_edit(event, message, buttons=buttons)
        
        elif data.startswith("ticket_transcript_"):
            if not is_admin(user_id):
                await event.answer("❌ Admin only!", alert=True)
                return
            
            ticket_id = data.replace("ticket_transcript_", "")
            ticket = get_ticket(ticket_id)
            
            if not ticket:
                await event.answer("❌ Ticket not found", alert=True)
                return
            
            transcript_file = f"transcripts/{ticket_id}_transcript.txt"
            
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(f"Support Ticket Transcript\n")
                f.write(f"Ticket ID: {ticket_id}\n")
                f.write(f"User: {ticket['user_name']} (ID: {ticket['user_id']})\n")
                f.write(f"Question: {ticket['question']}\n")
                f.write(f"Status: {ticket['status']}\n")
                f.write(f"Created: {ticket['timestamp']}\n")
                f.write("=" * 50 + "\n\n")
                
                for msg in ticket['messages']:
                    f.write(f"[{msg['timestamp']}] {msg['from'].upper()}: {msg['text']}\n")
            
            await bot.send_file(user_id, transcript_file, caption=f"📄 <b>Transcript:</b> {ticket_id}", parse_mode='html')
            
            await event.answer("✅ Transcript sent", alert=False)
    
    except Exception as e:
        log_error(f"Callback error for {data}", e)
        try:
            await event.answer("❌ An error occurred. Check logs.", alert=True)
        except:
            pass

# Start bot
print("\n" + "="*60)
print("🚀 BOT STARTING...")
print("="*60)
print(f"👤 Admin IDs: {', '.join(map(str, ADMIN_IDS))}")
print(f"👥 Group ID: {GROUP_ID}")
print(f"⭐ Vouches Channel: {VOUCHES_CHANNEL_ID}")
print(f"📦 Orders Channel: {ORDERS_CHANNEL_ID}")
print(f"💳 Payment Channel: {PAYMENT_NOTIFICATION_CHANNEL}")
print(f"🌍 Regions: {len(STORES)}")
total_stores = sum(len(store_data['stores']) for region in STORES.values() for store_data in region['categories'].values())
print(f"🏪 Total Stores: {total_stores}")
print(f"📦 Boxing Services: {len(BOXING_SERVICES)}")
print("="*60)
print("⚠️  IMPORTANT: Replace OXAPAY_API_KEY and OXAPAY_MERCHANT_ID with your actual credentials!")
print("="*60)
print("✅ BOT IS RUNNING! Errors will be logged below:")
print("="*60 + "\n")

# Start background tasks
loop = asyncio.get_event_loop()
loop.create_task(raffle_monitor())
loop.create_task(verification_cleanup())
loop.create_task(ticket_expiration_monitor())

# Run bot
bot.run_until_disconnected()