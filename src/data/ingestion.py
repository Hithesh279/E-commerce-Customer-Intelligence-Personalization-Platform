"""
src/data/ingestion.py
Synthetic data generator creating realistic e-commerce datasets with customer profiles,
product catalogs, transactional records, multi-aspect reviews, and behavioral interaction sequences.
Injects controlled data quality anomalies into raw tables for cleaning demonstration.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

from src.utils.config import (
    ASPECT_LIST,
    RANDOM_SEED,
    RAW_DATA_DIR,
    SCALE_CUSTOMERS,
    SCALE_INTERACTIONS,
    SCALE_PRODUCTS,
    SCALE_REVIEWS,
    SCALE_TRANSACTIONS,
    ensure_directories,
    load_config,
)
from src.utils.logging import get_logger

logger = get_logger("data_ingestion")

# Seed setup
np.random.seed(RANDOM_SEED)

# Domain Knowledge Dictionaries
CATEGORIES_METADATA = {
    "Electronics": {
        "subcategories": ["Smartphones", "Laptops", "Tablets", "Smart Monitors", "Power Banks"],
        "brands": ["ApexTech", "NovaByte", "VoltPro", "QuantumTech"],
        "price_range": (49.99, 1199.99),
    },
    "Clothing": {
        "subcategories": ["Activewear", "Winter Jackets", "Denim Jeans", "Formal Shirts", "Cotton Tees"],
        "brands": ["UrbanStitch", "AuraFit", "EcoThread", "VeloceWear"],
        "price_range": (19.99, 189.99),
    },
    "Home & Kitchen": {
        "subcategories": ["Espresso Machines", "Air Fryers", "Robot Vacuums", "Chef Knives", "Cookware Sets"],
        "brands": ["ChefCraft", "ZenLiving", "AuraHome", "CulinaryPro"],
        "price_range": (29.99, 399.99),
    },
    "Beauty": {
        "subcategories": ["Hydrating Serums", "Vitamin C Creams", "Mineral Sunscreens", "Hair Treatment Masks"],
        "brands": ["GlowBotanics", "DermaPure", "RadiantSkin", "LuxeEssence"],
        "price_range": (14.99, 119.99),
    },
    "Sports": {
        "subcategories": ["Running Shoes", "Yoga Mats", "Resistance Bands", "Smart Water Bottles", "Trekking Poles"],
        "brands": ["TerraGrip", "AeroFit", "PeakAthletics", "StrideMaster"],
        "price_range": (22.99, 249.99),
    },
    "Books": {
        "subcategories": ["Data Science & AI", "Business Strategy", "Science Fiction", "Mindfulness", "Biographies"],
        "brands": ["ApexPress", "InsightBooks", "VanguardPub", "HorizonMedia"],
        "price_range": (12.99, 65.00),
    },
    "Accessories": {
        "subcategories": ["Leather Wallets", "Polarized Sunglasses", "Canvas Backpacks", "Smart Keychains"],
        "brands": ["NomadCraft", "UrbanStep", "Vanguard", "TimberPeak"],
        "price_range": (18.99, 149.99),
    },
}

CITIES_DATA = [
    ("New York", "United States"), ("San Francisco", "United States"),
    ("Austin", "United States"), ("Seattle", "United States"),
    ("Chicago", "United States"), ("Toronto", "Canada"),
    ("Vancouver", "Canada"), ("London", "United Kingdom"),
    ("Berlin", "Germany"), ("Sydney", "Australia"),
]

MEMBERSHIP_TYPES = ["Bronze", "Silver", "Gold", "Platinum"]
CUSTOMER_SEGMENTS = ["High Value", "Regular", "Occasional", "Discount Sensitive", "At Risk", "New Customer"]

ASPECT_PHRASES = {
    "battery": {
        "pos": ["exceptional battery life that lasts over 48 hours", "battery performance exceeded expectations"],
        "neg": ["terrible battery draining in under 3 hours", "battery charges sluggishly and dies quickly"],
        "neu": ["average battery life sufficient for daily errands"],
    },
    "camera": {
        "pos": ["crystal clear camera resolution with vivid colors", "crisp camera lens capturing great details"],
        "neg": ["blurry camera quality in low light", "noisy camera sensor and disappointing zoom"],
        "neu": ["adequate camera for basic photography"],
    },
    "display": {
        "pos": ["vibrant and ultra-bright display with rich contrast", "stunning screen panel with smooth refresh rate"],
        "neg": ["dim display screen with severe outdoor glare", "washed out colors and dull display"],
        "neu": ["standard display clarity as expected"],
    },
    "performance": {
        "pos": ["blazing fast performance with zero latency", "incredibly responsive performance and swift multitasking"],
        "neg": ["sluggish performance prone to stutter and lag", "disappointing performance slowing down under load"],
        "neu": ["performance is acceptable for routine operations"],
    },
    "quality": {
        "pos": ["premium craftsmanship and rock-solid build quality", "exceptional material quality with luxurious finish"],
        "neg": ["cheap plastic build quality that feels delicate", "poor craftsmanship with fragile construction"],
        "neu": ["fair build quality in line with its market price"],
    },
    "price": {
        "pos": ["remarkable value for money and very reasonable price", "fairly priced offering great cost-benefit balance"],
        "neg": ["heavily overpriced considering the modest features", "poor value for money and expensive"],
        "neu": ["price is moderate and competitive"],
    },
    "comfort": {
        "pos": ["ergonomically designed and comfortable for extended hours", "super lightweight with soothing comfort"],
        "neg": ["awkward ergonomic fit causing soreness and discomfort", "uncomfortable to wear or use"],
        "neu": ["standard comfort level neither plush nor abrasive"],
    },
    "durability": {
        "pos": ["highly durable construction that withstands heavy wear", "rugged durability built to last for years"],
        "neg": ["lacks durability and fractured after a couple of weeks", "durability issues with rapid wear and tear"],
        "neu": ["appears durable enough for standard handling"],
    },
    "delivery": {
        "pos": ["ultra-fast delivery arriving two days before schedule", "prompt shipping with transparent tracking"],
        "neg": ["unacceptable delivery delays taking two extra weeks", "courier shipping was late and poorly communicated"],
        "neu": ["delivery took standard expected timeframe"],
    },
    "packaging": {
        "pos": ["secure eco-friendly packaging protecting contents impeccably", "elegant unboxing presentation and sturdy packaging"],
        "neg": ["damaged exterior packaging with dented corners", "flimsy packaging without protective padding"],
        "neu": ["arrived in standard cardboard packaging"],
    },
    "design": {
        "pos": ["sleek modern design with minimalist aesthetic", "visually appealing design drawing compliments"],
        "neg": ["clunky outdated design that looks uninspired", "awkward aesthetic design that feels bulky"],
        "neu": ["functional design without notable flair"],
    },
}


def generate_customers(n_customers: int) -> pd.DataFrame:
    """Generate customer demographics and behavioral segment attributes."""
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 6, 30)
    total_days = (end_date - start_date).days

    categories = list(CATEGORIES_METADATA.keys())
    records = []

    for i in range(1, n_customers + 1):
        signup_dt = start_date + timedelta(days=int(np.random.uniform(0, total_days)))
        city_pair = CITIES_DATA[np.random.choice(len(CITIES_DATA))]
        
        # Segment and membership assignment
        segment = np.random.choice(
            CUSTOMER_SEGMENTS,
            p=[0.12, 0.32, 0.24, 0.16, 0.08, 0.08]
        )
        if segment == "High Value":
            membership = np.random.choice(["Gold", "Platinum"], p=[0.40, 0.60])
        elif segment == "Regular":
            membership = np.random.choice(["Silver", "Gold"], p=[0.70, 0.30])
        elif segment == "Discount Sensitive":
            membership = np.random.choice(["Bronze", "Silver"], p=[0.75, 0.25])
        else:
            membership = np.random.choice(["Bronze", "Silver"], p=[0.85, 0.15])

        age = int(np.clip(np.random.normal(37, 11), 18, 75))
        gender = np.random.choice(["Female", "Male", "Non-Binary"], p=[0.49, 0.48, 0.03])
        preferred_cat = np.random.choice(categories)

        records.append({
            "customer_id": f"CUST_{i:05d}",
            "gender": gender,
            "age": age,
            "city": city_pair[0],
            "country": city_pair[1],
            "membership_type": membership,
            "signup_date": signup_dt.strftime("%Y-%m-%d"),
            "customer_segment": segment,
            "preferred_category": preferred_cat,
        })

    df = pd.DataFrame(records)
    logger.info(f"Generated {len(df)} customer records.")
    return df


def generate_products(n_products: int) -> pd.DataFrame:
    """Generate rich product catalog across all categories."""
    categories = list(CATEGORIES_METADATA.keys())
    adjectives = ["Ultra", "Pro", "Smart", "Classic", "Hyper", "Elite", "Active", "Eco", "Vanguard", "Signature"]
    nouns = ["Edge", "Core", "Sense", "Wave", "Flow", "Max", "Prime", "Studio", "Fusion", "Glide"]

    records = []
    prod_idx = 1
    while prod_idx <= n_products:
        cat = categories[(prod_idx - 1) % len(categories)]
        meta = CATEGORIES_METADATA[cat]
        subcat = np.random.choice(meta["subcategories"])
        brand = np.random.choice(meta["brands"])
        adj = np.random.choice(adjectives)
        noun = np.random.choice(nouns)
        num = np.random.randint(100, 999)
        name = f"{brand} {adj} {noun} {num} {subcat}"

        raw_price = np.random.uniform(meta["price_range"][0], meta["price_range"][1])
        price = round(raw_price, 2)

        description = (
            f"The {name} is engineered for peak performance in {subcat.lower()} category. "
            f"Crafted by {brand} featuring cutting-edge durability, ergonomic comfort, and sleek design. "
            f"Combines superior quality materials with modern technology for daily efficiency and reliable longevity."
        )

        records.append({
            "product_id": f"PROD_{prod_idx:04d}",
            "product_name": name,
            "category": cat,
            "subcategory": subcat,
            "brand": brand,
            "price": price,
            "product_description": description,
        })
        prod_idx += 1

    df = pd.DataFrame(records)
    logger.info(f"Generated {len(df)} product catalog records.")
    return df


def generate_transactions(
    customers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    n_transactions: int,
) -> pd.DataFrame:
    """Generate transactional sales history with mathematically consistent pricing and return rates."""
    customer_ids = customers_df["customer_id"].tolist()
    product_ids = products_df["product_id"].tolist()
    price_map = dict(zip(products_df["product_id"], products_df["price"]))
    
    # Power-law popularity for products
    ranks = np.arange(1, len(product_ids) + 1)
    popularity_weights = 1.0 / (ranks ** 0.75)
    
    # Intentionally skew PROD_0005 (high sales, poor sentiment/returns) and PROD_0025 (low sales, high sentiment)
    popularity_weights[4] *= 5.0  # PROD_0005
    popularity_weights[24] *= 0.15 # PROD_0025
    popularity_weights /= popularity_weights.sum()

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    total_seconds = int((end_date - start_date).total_seconds())

    payment_methods = ["Credit Card", "PayPal", "Debit Card", "Apple Pay", "Gift Card"]
    pm_weights = [0.45, 0.25, 0.15, 0.10, 0.05]

    records = []
    for i in range(1, n_transactions + 1):
        cid = np.random.choice(customer_ids)
        pid = np.random.choice(product_ids, p=popularity_weights)
        sec_offset = int(np.random.uniform(0, total_seconds))
        txn_dt = start_date + timedelta(seconds=sec_offset)

        unit_price = price_map[pid]
        quantity = int(np.random.choice([1, 2, 3, 4], p=[0.74, 0.18, 0.06, 0.02]))
        discount_pct = float(np.random.choice([0.0, 5.0, 10.0, 15.0, 20.0], p=[0.55, 0.18, 0.14, 0.08, 0.05]))
        
        # Exact arithmetic computation
        discount_amount = round((quantity * unit_price) * (discount_pct / 100.0), 2)
        total_amount = round((quantity * unit_price) - discount_amount, 2)
        
        # Realistic return status
        if pid == "PROD_0005":
            return_status = np.random.choice(["Returned", "Completed"], p=[0.34, 0.66])
        elif pid == "PROD_0025":
            return_status = np.random.choice(["Returned", "Completed"], p=[0.02, 0.98])
        else:
            return_status = np.random.choice(["Returned", "Completed", "Pending"], p=[0.07, 0.90, 0.03])

        payment_method = np.random.choice(payment_methods, p=pm_weights)

        records.append({
            "transaction_id": f"TXN_{i:06d}",
            "customer_id": cid,
            "product_id": pid,
            "transaction_date": txn_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_percentage": discount_pct,
            "discount_amount": discount_amount,
            "total_amount": total_amount,
            "payment_method": payment_method,
            "return_status": return_status,
        })

    df = pd.DataFrame(records)
    df = df.sort_values("transaction_date").reset_index(drop=True)
    logger.info(f"Generated {len(df)} transaction records.")
    return df


REALISTIC_REVIEWS_CORPUS = [
    # 75 Negative Reviews (Compound multi-aspect & authentic consumer complaints)
    (2, "Good display, great camera and very bad durability and bad battery performance."),
    (2, "Great screen and nice design, but terrible battery life and slow charging."),
    (1, "Good camera, but very bad durability and broke after one week."),
    (2, "Display is great, but performance is bad and battery drains fast."),
    (1, "Nice packaging, but terrible product quality and waste of money."),
    (2, "Comfortable to wear, but terrible sound quality and bad connection."),
    (2, "Good price, but very bad quality and feels very cheap."),
    (1, "Fast delivery, but defective item and broken on arrival."),
    (2, "Good design, but awful battery performance and heating issues."),
    (2, "Great sound, but very bad build quality and fragile plastic."),
    (2, "Display looks sharp, but constant stuttering, lag, and awful battery drain."),
    (2, "Decent camera in daylight, but horrible night photos and terrible battery life."),
    (1, "Sleek modern design, but terrible durability and cracked after a tiny bump."),
    (1, "Good looking jacket, but cheap zipper that broke immediately and poor fabric."),
    (1, "Nice color and comfortable fit, but seam ripped after the very first wash."),
    (1, "Packaging was elegant, but the product inside was completely defective and useless."),
    (2, "Good screen brightness, but terrible software bugs and unusable performance."),
    (2, "Comfortable ear cushions, but terrible microphone quality and constant static."),
    (1, "Affordable price tag, but very bad customer support and broken charging port."),
    (2, "Looks stylish on the wrist, but terrible sensor accuracy and awful battery."),
    (1, "Very bad durability and bad battery performance, do not buy!"),
    (1, "Terrible quality, broke in two days. Complete waste of money."),
    (1, "Horrible customer service and defective product. Extremely disappointed."),
    (1, "Bad camera, bad battery, terrible display. Worst purchase ever."),
    (1, "Awful performance, constantly freezing and super slow."),
    (1, "Poor build quality, cheap materials, very bad experience."),
    (1, "Complete waste of money. Died after two days and refused to charge."),
    (1, "Defective unit out of the box. Battery will not charge past 10 percent."),
    (1, "Terrible sound with awful buzzing noise in the right ear. Returning immediately."),
    (1, "Cheap flimsy plastic. Dropped from couch height and shattered into pieces."),
    (1, "Horrible product. Stopped working within one week of normal usage."),
    (1, "Do not buy this! It overheated within 30 minutes and shut down."),
    (1, "Extremely disappointed. Terrible quality control and missing accessories in box."),
    (1, "Worst customer support ever. They refused to replace a defective unit."),
    (1, "Battery drains completely in less than 2 hours. Completely unusable for work."),
    (1, "Awful lag and stutter. Apps crash constantly, terrible operating speed."),
    (1, "Terrible experience. The stitching came undone and the fabric feels like sandpaper."),
    (1, "Fragile and cheap. The power button broke after just three clicks."),
    (1, "Horrendous audio quality. Sounds muffled, distorted, and hollow."),
    (1, "Total rip off. Overpriced and broke immediately. Stay far away."),
    (1, "Not worth even 10 dollars. Terrible battery life, terrible camera, and laggy."),
    (1, "Flimsy build quality and loud annoying fan noise. Very bad purchase."),
    (1, "Disastrous purchase. The screen started flickering violently on day 3."),
    (1, "Arrived with a dented corner and scratched screen. Unacceptable packaging."),
    (1, "Terrible durability. Handle snapped off while using it normally."),
    (1, "Very disappointed with the build quality. Rattles and feels like cheap junk."),
    (1, "Terrible battery life. I have to recharge it three times a day."),
    (1, "Broke after two weeks of light use. Customer service refused to honor warranty."),
    (1, "Sluggish performance and constant freezing. Completely unsuited for multitasking."),
    (1, "Garbage product. Does not work as advertised at all."),
    (1, "Uncomfortable and awkward fit. Gave me headaches after only 15 minutes."),
    (1, "Severe lag, terrible display resolution, and atrocious battery performance."),
    (1, "Poor quality materials that smell bad and feel fragile. Regret buying."),
    (1, "Fell apart on day four. Save your hard-earned money and buy something else."),
    (1, "Terrible connectivity. Drops bluetooth every 2 minutes. Infuriating to use."),
    (1, "The vacuum motor burned out after three cleanings. Terrible reliability."),
    (1, "The espresso machine leaked water all over my counter. Defective seals."),
    (1, "Very cheap plastic construction. Buttons get stuck constantly."),
    (1, "Horrible lag when opening apps. Performance is reminiscent of ten-year-old tech."),
    (1, "Battery dies in 3 hours even on power saver mode. Waste of money."),
    (1, "Disappointing quality, terrible durability, and zero support from seller."),
    (1, "The display has dead pixels right in the center. Very poor quality control."),
    (1, "Awful microphone. Everyone told me I sounded like I was underwater."),
    (1, "The zipper jammed and tore the jacket fabric on my second day wearing it."),
    (1, "Broke during normal assembly. The plastic clips are extremely brittle."),
    (1, "Terrible product. Scratches easily, charges slowly, and dies fast."),
    (1, "Fails to connect to wifi half the time. Extremely frustrating and slow."),
    (1, "Poorly engineered. Overheats dangerously during light browsing."),
    (1, "Defective charger and battery life is a joke. Very bad product."),
    (1, "Unusable. Touchscreen is unresponsive and misses half my taps."),
    (1, "Cheaply made, noisy, and broke after one week. Total disappointment."),
    (1, "Very bad durability. Sole detached from the running shoe after 10 miles."),
    (1, "Terrible purchase. The serum caused irritation and smells awful."),
    (1, "Broke right after return window closed. Cheap components and bad design."),
    (1, "One star is too generous. Defective, flimsy, and terrible performance."),

    # 50 Neutral / Balanced Reviews
    (3, "Good display and great camera, but average battery and okay durability."),
    (3, "Decent product for the price. Average performance and standard battery."),
    (3, "Acceptable quality, neither great nor bad. Standard features."),
    (3, "Fair build and decent camera, but delivery took a bit longer than expected."),
    (3, "Product is okay for simple daily tasks, but nothing special."),
    (3, "Average build quality. Screen is decent, but battery life is mediocre."),
    (3, "It works as described, but does not stand out in any particular aspect."),
    (3, "Adequate performance for routine web browsing. Battery lasts around 6 hours."),
    (3, "Decent design and acceptable comfort, though sound quality is just average."),
    (3, "The packaging was okay. Product works fine, neither impressed nor disappointed."),
    (3, "Standard quality for this price range. Expected a bit more, but it is acceptable."),
    (3, "Performance is acceptable for routine tasks. Display is fine for office work."),
    (3, "Average sound quality. Good for podcasts, but music sounds just okay."),
    (3, "Decent fit and reasonable comfort. Durability remains to be tested over time."),
    (3, "It does the job, but do not expect premium features or lightning speed."),
    (3, "Average battery life. Lasts a typical workday with moderate usage."),
    (3, "Fair product overall. Some minor quirks, but acceptable value for money."),
    (3, "Decent camera in good lighting, but average in dim environments."),
    (3, "Packaging was standard cardboard. The item arrived in one piece and works ok."),
    (3, "Neutral feeling about this purchase. Works reasonably well without surprises."),
    (3, "Average comfort, decent stitching, but nothing luxurious about the material."),
    (3, "Acceptable responsiveness. Occasional micro-stutter, but nothing major."),
    (3, "Reasonable price for the specifications. Performance is about what I expected."),
    (3, "It is an okay product. Neither blown away nor terribly upset."),
    (3, "Average display brightness. Good indoors, but slightly dim in direct sunlight."),
    (3, "Standard battery charging time. Takes about 2 hours for a full charge."),
    (3, "Decent vacuum suction for tile floors, but average performance on thick carpets."),
    (3, "Acceptable espresso taste. Crema is modest, but acceptable for home use."),
    (3, "Moderate quality build. Plastic feels okay, but not premium metal."),
    (3, "Fairly comfortable for an hour or two, but slightly tight after longer wear."),
    (3, "Basic product that gets routine chores done. Standard reliability so far."),
    (3, "Middle of the road performance. Fast enough for daily apps, not for heavy games."),
    (3, "Acceptable delivery timeframe and standard packaging. Product works as expected."),
    (3, "Decent water bottle. Keeps drinks cool for around 6 hours, which is fair."),
    (3, "The jacket is okay for autumn, but not warm enough for severe winter."),
    (3, "Decent screen colors, standard 60Hz refresh rate, acceptable viewing angles."),
    (3, "Fair value. There are slightly better options, but this one is acceptable."),
    (3, "Moderate battery drain. You will need to charge it every night."),
    (3, "Acceptable sound clarity at moderate volume, but distorts at max volume."),
    (3, "Standard durability so far. Has handled daily commute without issues."),
    (3, "Decent quality fabric, standard stitching, fit is true to size."),
    (3, "Neither satisfied nor dissatisfied. It is a standard mid-range device."),
    (3, "Average camera sharpness. Good enough for social media, not professional."),
    (3, "Product performs adequately. Meets baseline expectations without fanfare."),
    (3, "Acceptable noise cancellation. Cuts low hums, but voices still pass through."),
    (3, "Decent finish and acceptable ergonomics. Average battery longevity."),
    (3, "Average product. Fair price and acceptable performance for regular needs."),
    (3, "Standard quality control. A few minor cosmetic blemishes, but functions ok."),
    (3, "Decent comfort for short walks, though cushioning is on the firmer side."),
    (3, "Acceptable performance and decent value for budget-conscious buyers."),

    # 75 Positive Reviews
    (5, "Good display, great camera, excellent battery and fast performance!"),
    (5, "Amazing build quality, great durability and superb battery life."),
    (5, "Totally worth the price! Blazing fast, beautiful screen and great design."),
    (5, "Super happy with this purchase! Fast delivery, great quality, highly recommend."),
    (5, "Great camera, good battery life, comfortable and very durable."),
    (5, "Excellent sound, crystal clear display, fast shipping and beautiful packaging."),
    (5, "Love this product! Premium materials, superb performance and very reliable."),
    (5, "Best purchase I made all year! Incredible value, awesome battery life."),
    (5, "Outstanding craftsmanship! Sleek design, ultra-fast charging, and gorgeous screen."),
    (5, "Blazing fast performance with zero lag. Beautiful OLED screen and rich colors."),
    (5, "Battery lasts two full days on a single charge! Truly impressive engineering."),
    (5, "Top notch build quality. Feels rugged, durable, and luxurious in hand."),
    (5, "Remarkable sound quality with deep punchy bass and crystal clear vocals."),
    (5, "Exceeded all my expectations! Highly responsive, intuitive, and beautifully built."),
    (5, "Incredible camera resolution. The detail and color accuracy are astonishing."),
    (5, "Extremely comfortable to wear all day. Lightweight and ergonomic design."),
    (5, "Arrived within 24 hours in pristine packaging. Five stars all the way!"),
    (5, "Superb value for money! Competes easily with products twice its price."),
    (5, "Whisper quiet operation and lightning-fast speed. Very pleased with this purchase."),
    (5, "Fantastic battery longevity and super fast charging. Highly recommended!"),
    (5, "The display is absolutely breathtaking. Razor sharp text and vivid HDR colors."),
    (5, "Premium anodized aluminum finish. Super sturdy and elegant modern design."),
    (5, "The espresso machine brews rich, authentic coffee with gorgeous thick crema."),
    (5, "Robot vacuum navigates around furniture effortlessly and picks up all pet hair."),
    (5, "Nonstick cookware set is an absolute dream to cook with and cleans in seconds."),
    (5, "Running shoes have exceptional cushioning and superb traction on wet trails."),
    (5, "Serum made my skin glowing and radiant after just one week of daily use."),
    (5, "Crystal clear calls, superb active noise cancellation, and seamless Bluetooth."),
    (5, "The jacket is exceptionally warm, lightweight, and completely windproof."),
    (5, "Denim jeans fit like a glove, super flexible stretch, and very durable."),
    (4, "Incredible screen refresh rate. Gaming and scrolling feel buttery smooth."),
    (5, "A fantastic upgrade! Everything works flawlessly out of the box."),
    (5, "Super sturdy construction that feels like it will last for a decade."),
    (5, "Battery life is astounding! Easily survives my heavy 14-hour workdays."),
    (5, "Delighted with the build quality and performance. Worth every single penny."),
    (5, "Amazing packaging and swift delivery. The unboxing experience was top tier."),
    (5, "Vibrant OLED colors, outstanding contrast, and zero backlight bleeding."),
    (5, "Super responsive touchscreen with instant app launches and zero stutter."),
    (5, "Super comfortable cushioning. My back pain disappeared after switching to this."),
    (4, "Great price for such premium quality. Will definitely purchase again."),
    (5, "Incredible camera zoom and low-light night mode. Pictures look stunning."),
    (5, "Lightweight, sleek, and exceptionally durable. Perfect travel companion."),
    (5, "Flawless performance under heavy multitasking. Never breaks a sweat."),
    (5, "Beautiful minimalist design that looks gorgeous on my work desk."),
    (5, "Battery charges to 80 percent in under 30 minutes. Super convenient!"),
    (5, "Outstanding durability. Survived multiple drops without a single scratch."),
    (5, "The audio separation and soundstage are unbelievable for this price."),
    (4, "Super clean packaging with thoughtful eco-friendly paper wrapping."),
    (5, "Reliable, fast, and remarkably well built. Truly five-star product."),
    (5, "Love the ergonomic design. Fits naturally in my hand with zero fatigue."),
    (5, "The material quality is exceptional. Soft to the touch and very durable."),
    (5, "Air fryer cooks fries to crispy perfection in half the usual time."),
    (5, "Yoga mat has incredible grip and perfect thickness for joints. Love it!"),
    (5, "Hydration bottle keeps water ice-cold for over 24 hours. Super durable."),
    (4, "Fast delivery, great communication, and product works like a charm."),
    (5, "Impressive battery efficiency. I only need to charge it once a week."),
    (5, "The camera dynamic range is spectacular. Captures sunset hues perfectly."),
    (5, "Solid build, snappy performance, and gorgeous display. 10/10 purchase."),
    (5, "Highly durable fabric and precision stitching. Looks and feels luxurious."),
    (5, "Phenomenal customer experience. Product exceeded all my high expectations."),
    (5, "Blazing fast boot times and flawless multitasking. Extremely happy."),
    (5, "Great noise isolation and supreme audio fidelity. Pure listening joy."),
    (4, "Super easy setup. Connected to my phone in 5 seconds and works perfectly."),
    (5, "Rich colors, sharp contrast, and gentle on the eyes during long sessions."),
    (5, "Exceptional value! High-end performance at an affordable, fair price."),
    (5, "The battery life alone makes this worth buying. Truly unmatched longevity."),
    (5, "Beautiful aesthetics and premium build quality. Everyone compliments it."),
    (4, "Super fast shipping, impeccable condition, and outstanding performance."),
    (5, "Rugged, reliable, and beautifully engineered. Highly satisfied customer."),
    (5, "Pristine unboxing experience and stellar build. A triumph of design."),
    (5, "Camera autofocus is lightning fast and tack sharp. Love taking photos with it."),
    (5, "Incredible comfort and featherlight weight. You barely feel it is there."),
    (5, "Magnificent product. Flawless execution across every single aspect."),
    (5, "Top tier durability, superb battery, and blazing speed. Absolutely thrilled!"),
    (5, "Five stars! Exceptional quality, beautiful design, and top performance."),
]


def generate_reviews(
    transactions_df: pd.DataFrame,
    n_reviews: int,
) -> pd.DataFrame:
    """Generate realistic, human customer reviews from curated corpus covering all 11 aspects."""
    sample_txns = transactions_df.sample(n=n_reviews, replace=True, random_state=RANDOM_SEED).reset_index(drop=True)
    n_corpus = len(REALISTIC_REVIEWS_CORPUS)

    records = []
    for idx, row in sample_txns.iterrows():
        pid = row["product_id"]
        cid = row["customer_id"]
        txn_dt = datetime.strptime(row["transaction_date"], "%Y-%m-%d %H:%M:%S")
        review_dt = txn_dt + timedelta(days=int(np.random.randint(1, 14)), hours=int(np.random.randint(1, 23)))

        # Cycle through or sample from realistic corpus
        corpus_idx = idx % n_corpus
        rating, review_text = REALISTIC_REVIEWS_CORPUS[corpus_idx]

        records.append({
            "review_id": f"REV_{idx + 1:06d}",
            "customer_id": cid,
            "product_id": pid,
            "review_date": review_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "rating": rating,
            "review_text": review_text,
        })

    df = pd.DataFrame(records)
    df = df.sort_values("review_date").reset_index(drop=True)
    logger.info(f"Generated {len(df)} realistic customer review records.")
    return df


def generate_interactions(
    transactions_df: pd.DataFrame,
    customers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    n_interactions: int,
) -> pd.DataFrame:
    """Generate realistic browsing interaction sequences (view -> click -> wishlist -> cart -> purchase)."""
    records = []
    inter_idx = 1

    # 1. Purchase flow interactions linked to actual transactions
    # Each purchase flow emits 4 events (view, click, cart, purchase). Choose enough flows to use
    # about 40% of the configured interaction budget, so the total stays at n_interactions.
    n_flows = min(len(transactions_df), int(n_interactions * 0.40) // 4)
    sample_txns = transactions_df.sample(n=n_flows, random_state=RANDOM_SEED)
    for _, row in sample_txns.iterrows():
        t_dt = datetime.strptime(row["transaction_date"], "%Y-%m-%d %H:%M:%S")
        sess_id = f"SESS_{row['customer_id']}_{t_dt.strftime('%Y%m%d%H')}"

        v_dt = t_dt - timedelta(minutes=int(np.random.randint(15, 60)))
        c_dt = t_dt - timedelta(minutes=int(np.random.randint(5, 14)))
        cart_dt = t_dt - timedelta(minutes=int(np.random.randint(1, 4)))

        records.append({"interaction_id": f"INT_{inter_idx:07d}", "customer_id": row["customer_id"], "product_id": row["product_id"], "interaction_type": "view", "timestamp": v_dt.strftime("%Y-%m-%d %H:%M:%S"), "session_id": sess_id})
        inter_idx += 1
        records.append({"interaction_id": f"INT_{inter_idx:07d}", "customer_id": row["customer_id"], "product_id": row["product_id"], "interaction_type": "click", "timestamp": c_dt.strftime("%Y-%m-%d %H:%M:%S"), "session_id": sess_id})
        inter_idx += 1
        records.append({"interaction_id": f"INT_{inter_idx:07d}", "customer_id": row["customer_id"], "product_id": row["product_id"], "interaction_type": "cart", "timestamp": cart_dt.strftime("%Y-%m-%d %H:%M:%S"), "session_id": sess_id})
        inter_idx += 1
        records.append({"interaction_id": f"INT_{inter_idx:07d}", "customer_id": row["customer_id"], "product_id": row["product_id"], "interaction_type": "purchase", "timestamp": row["transaction_date"], "session_id": sess_id})
        inter_idx += 1

    # 2. Browsing and discovery interactions
    remaining = n_interactions - len(records)
    customer_ids = customers_df["customer_id"].tolist()
    product_ids = products_df["product_id"].tolist()
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    total_seconds = int((end_date - start_date).total_seconds())

    for _ in range(max(0, remaining)):
        cid = np.random.choice(customer_ids)
        pid = np.random.choice(product_ids)
        sec_offset = int(np.random.uniform(0, total_seconds))
        i_dt = start_date + timedelta(seconds=sec_offset)
        sess_id = f"SESS_{cid}_{i_dt.strftime('%Y%m%d%H')}"
        itype = np.random.choice(["view", "click", "wishlist"], p=[0.60, 0.28, 0.12])

        records.append({
            "interaction_id": f"INT_{inter_idx:07d}",
            "customer_id": cid,
            "product_id": pid,
            "interaction_type": itype,
            "timestamp": i_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": sess_id,
        })
        inter_idx += 1

    df = pd.DataFrame(records)
    df = df.sort_values("timestamp").reset_index(drop=True)
    if len(df) != n_interactions:
        logger.warning(f"Generated {len(df)} interactions; configured target was {n_interactions}.")
    logger.info(f"Generated {len(df)} interaction sequence records.")
    return df


def inject_controlled_anomalies(dataset: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Inject small, controlled, realistic data quality anomalies into raw tables.
    Demonstrates professional data cleansing practices.
    """
    logger.info("Injecting controlled data quality anomalies into raw tables...")
    raw_data = {k: v.copy() for k, v in dataset.items()}

    # 1. Null values in a non-critical column (customers.age)
    cust = raw_data["customers"]
    null_idx = cust.sample(frac=0.015, random_state=RANDOM_SEED).index
    cust.loc[null_idx, "age"] = np.nan

    # 2. Slight duplicates (< 0.4%)
    txns = raw_data["transactions"]
    dup_sample = txns.sample(n=min(len(txns), 50), random_state=RANDOM_SEED)
    raw_data["transactions"] = pd.concat([txns, dup_sample], ignore_index=True)

    # 3. Inconsistent category casing in products table
    prod = raw_data["products"]
    casing_idx = prod.sample(frac=0.05, random_state=RANDOM_SEED).index
    prod.loc[casing_idx, "category"] = prod.loc[casing_idx, "category"].str.lower()

    logger.info("Anomalies injected: missing customer ages, duplicate transactions, inconsistent category casings.")
    return raw_data


def generate_and_save_dataset() -> Dict[str, pd.DataFrame]:
    """Orchestrate data generation and export raw CSVs."""
    ensure_directories()
    logger.info("Initializing synthetic dataset generation pipeline...")

    config = load_config()
    n_cust = config["data_generation"]["num_customers"]
    n_prod = config["data_generation"]["num_products"]
    n_txn = config["data_generation"]["num_transactions"]
    n_rev = config["data_generation"]["num_reviews"]
    n_int = config["data_generation"]["num_interactions"]

    customers_df = generate_customers(n_cust)
    products_df = generate_products(n_prod)
    transactions_df = generate_transactions(customers_df, products_df, n_txn)
    reviews_df = generate_reviews(transactions_df, n_rev)
    interactions_df = generate_interactions(transactions_df, customers_df, products_df, n_int)

    clean_data = {
        "customers": customers_df,
        "products": products_df,
        "transactions": transactions_df,
        "reviews": reviews_df,
        "interactions": interactions_df,
    }

    raw_data = inject_controlled_anomalies(clean_data)

    # Save to data/raw/
    for table_name, df in raw_data.items():
        file_path = RAW_DATA_DIR / f"{table_name}.csv"
        df.to_csv(file_path, index=False)
        logger.info(f"Exported raw table {table_name}: {file_path} ({len(df)} rows)")

    return raw_data


if __name__ == "__main__":
    generate_and_save_dataset()
